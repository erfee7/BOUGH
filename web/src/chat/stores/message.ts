import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { Message } from '@/types';
import { apiFetch } from '@/utils/api';
import { useConversationStore } from './conversation';
import { useGenerationConfigStore } from './generationConfig';
import { getActivePath, getSiblingInfo, getMostRecentDescendantLeaf, compareMessages } from '../branchingUtils';
import { loadLocalConfig, updateLocalConfig } from '../persistence';

export const useMessageStore = defineStore('message', () => {
    const conversationStore = useConversationStore();
    const generationConfigStore = useGenerationConfigStore();

    
    const messages = ref<Message[]>([]);
    const activeLeafId = ref<string | null>(null);
    // Derived: the composer is streaming iff the visible leaf is still being
    // generated. Listeners never write this — they only update message records.
    const isStreaming = computed(() => {
        const leaf = messages.value.find(m => m.id === activeLeafId.value);
        return !!leaf && (leaf.status === 'pending' || leaf.status === 'streaming');
    });

    // Adjustable UI refresh rate in milliseconds (0 = update on every token, 50 = 20fps)
    const streamRefreshInterval = ref(50);

    // Hydrate from local-config; invalid/missing leaves the store default (50) untouched
    const savedInterval = loadLocalConfig().streamRefreshInterval;
    if (savedInterval !== null) {
        streamRefreshInterval.value = savedInterval;
    }

    // Persist user changes (mirror, not navigation logic)
    watch(streamRefreshInterval, (value) => {
        updateLocalConfig({ streamRefreshInterval: value });
    });

    let abortController: AbortController | null = null;

    // --- Getters ---
    const activePath = computed(() => {
        return getActivePath(messages.value, activeLeafId.value);
    });

    // --- Actions ---

    // 0a. Detach the browser's SSE listener (aborts the HTTP request only —
    // the server-side generation keeps running)
    function stopStreaming() {
        if (abortController) {
            abortController.abort();
            abortController = null;
        }
    }

    // 0b. The centralized helper to change activeLeafId, with proper related operations
    function activateLeaf(messageId: string | null) {
        stopStreaming();
        activeLeafId.value = messageId;
        if (!messageId) return;
        const msg = messages.value.find(m => m.id === messageId);
        if (msg && (msg.status === 'pending' || msg.status === 'streaming')) {
            startStreaming(messageId);
        }
    }

    // 1. Load an existing conversation and its history
    async function loadConversation(conversationId: string) {
        try {
            const response = await apiFetch(`/api/chat/conversations/${conversationId}`);
            if (!response.ok) throw new Error('Failed to load conversation');
            
            const data = await response.json();
            messages.value = data.messages;
            activateLeaf(data.conversation.active_leaf_id);
        }
        catch (error) {
            console.error("Error loading conversation:", error);
        }
    }

    function clearMessages() {
        activateLeaf(null);
        messages.value = [];
    }

    // 2. User sends a new message
    async function sendMessage(content: string, developerContent: string | null = null, attachmentIds: string[] = []): Promise<string | null> {
        if (!activeLeafId.value || isStreaming.value) return null;
        
        try {
            let currentParentId = activeLeafId.value;
            
            // Step A: If developer prompt exists, append it first
            if (developerContent && developerContent.trim()) {
                const devResponse = await apiFetch(`/api/chat/messages/${currentParentId}/append`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: developerContent, role: 'developer' })
                });
                if (!devResponse.ok) throw new Error('Failed to append developer message');
                const devData = await devResponse.json();
                
                const devMsg: Message = {
                    id: devData.id,
                    parent_id: devData.parent_id,
                    role: devData.role,
                    content: devData.content,
                    reasoning: devData.reasoning ?? null,
                    attachments: devData.attachments ?? [],
                    status: devData.status,
                    creation_data: devData.creation_data,
                    error_data: devData.error_data,
                    metadata: devData.metadata,
                    created_at: devData.created_at
                };
                
                messages.value.push(devMsg);
                currentParentId = devMsg.id;
                activateLeaf(devMsg.id);
            }
            
            // Step B: Append the user message
            const response = await apiFetch(`/api/chat/messages/${currentParentId}/append`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, role: "user", attachment_ids: attachmentIds })
            });
            if (!response.ok) throw new Error('Failed to append message');
            const data = await response.json();
            
            const userMsg: Message = {
                id: data.id,
                parent_id: data.parent_id,
                role: data.role,
                content: data.content,
                reasoning: data.reasoning ?? null,
                attachments: data.attachments ?? [],
                status: data.status,
                creation_data: data.creation_data,
                error_data: data.error_data,
                metadata: data.metadata,
                created_at: data.created_at
            };
            
            messages.value.push(userMsg);
            activateLeaf(userMsg.id);
            
            // Step C: Trigger generation
            await generateMessage(userMsg.id);
            
            return userMsg.id;
        }
        catch (error) {
            console.error("Error sending message:", error);
            return null;
        }
    }

    // 3. Trigger LLM generation
    async function generateMessage(parentId: string) {
        try {
            const payload = generationConfigStore.buildGeneratePayload();
            const response = await apiFetch(`/api/chat/messages/${parentId}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload) 
            });
            
            if (!response.ok) throw new Error('Failed to start generation');
            const data = await response.json();
            
            const assistantMsg: Message = {
                id: data.id,
                parent_id: data.parent_id,
                role: data.role,
                content: data.content,
                reasoning: data.reasoning ?? null,
                attachments: data.attachments ?? [],
                status: data.status,
                creation_data: data.creation_data,
                error_data: data.error_data,
                metadata: data.metadata,
                created_at: data.created_at
            };
            
            messages.value.push(assistantMsg);
            activateLeaf(assistantMsg.id);

            // Bump the conversation to the top of the sidebar
            if (conversationStore.currentConversationId) {
                conversationStore.bumpLocalConversation(conversationStore.currentConversationId);
            }
        }
        catch (error) {
            console.error("Error generating message:", error);
        }
    }

    // 4. Attach the single SSE listener to read the stream
    async function startStreaming(messageId: string) {
        abortController = new AbortController();
        
        const decoder = new TextDecoder();
        
        let chunksBuffer = '';
        
        // --- Throttle Buffers ---
        let contentBuffer = '';
        let reasoningBuffer = '';
        let flushTimer: number | null = null;

        // Flushes buffered tokens to the reactive array when called (by timer or upon stream end)
        const flushBuffers = () => {
            const msgIndex = messages.value.findIndex(m => m.id === messageId);
            if (msgIndex === -1) return;

            let mutated = false;
            if (contentBuffer) {
                messages.value[msgIndex].content = (messages.value[msgIndex].content || '') + contentBuffer;
                contentBuffer = '';
                mutated = true;
            }
            if (reasoningBuffer) {
                messages.value[msgIndex].reasoning = (messages.value[msgIndex].reasoning || '') + reasoningBuffer;
                reasoningBuffer = '';
                mutated = true;
            }
            if (mutated && messages.value[msgIndex].status === 'pending') {
                messages.value[msgIndex].status = 'streaming';
            }
        };

        try {
            const response = await apiFetch(`/api/chat/messages/${messageId}/stream`, {
                signal: abortController.signal // Pass the signal to fetch
            });
            
            if (!response.body) throw new Error('No response body');
            
            const reader = response.body.getReader();
            
            // Start the throttled flusher if interval > 0
            if (streamRefreshInterval.value > 0) {
                // Sets a background timer to flush accumulated buffers periodically, reducing DOM updates
                flushTimer = window.setInterval(flushBuffers, streamRefreshInterval.value);
            }

            while (true) {
                // Read bytes from the TCP stream
                const { done, value } = await reader.read();
                
                if (done) break;
                
                // Convert bytes to string and add to our buffer
                chunksBuffer += decoder.decode(value, { stream: true });
                
                // SSE events are separated by a double newline
                const chunks = chunksBuffer.split('\n\n');
                
                // The last item might be an incomplete chunk, so we save it back to the buffer
                chunksBuffer = chunks.pop() || '';
                
                // Process all complete chunks
                for (const chunk of chunks) {
                    // Strip the "data: " prefix
                    if (!chunk.startsWith('data: ')) continue;
                    const jsonStr = chunk.replace('data: ', '');
                    
                    if (jsonStr === '[DONE]') {
                        // // Flush any remaining buffered content before exiting
                        // flushBuffers();
                        // if (flushTimer) clearInterval(flushTimer);
                        // flushTimer = null;
                        return;
                    }
                    
                    // Parse the JSON event
                    const event = JSON.parse(jsonStr);
                    
                    // Find the message we are updating in the reactive array
                    const msgIndex = messages.value.findIndex(m => m.id === messageId);
                    if (msgIndex !== -1) {
                        if (event.type === 'catch_up') {
                            // Reset buffers and assign directly to avoid duplication
                            contentBuffer = '';
                            reasoningBuffer = '';
                            messages.value[msgIndex].content = event.content || '';
                            messages.value[msgIndex].reasoning = event.reasoning || '';
                            messages.value[msgIndex].status = 'streaming';
                        } else if (event.type === 'token') {
                            // Append to buffer instead of mutating ref directly
                            contentBuffer += event.content;
                            // If interval is 0, flush immediately (no throttling)
                            if (streamRefreshInterval.value === 0) flushBuffers();
                        } else if (event.type === 'reasoning') {
                            // Append to buffer instead of mutating ref directly
                            reasoningBuffer += event.content;
                            // If interval is 0, flush immediately (no throttling)
                            if (streamRefreshInterval.value === 0) flushBuffers();
                        } else if (event.type === 'done') {
                            // Flush remaining tokens before applying final state
                            flushBuffers();
                            if (flushTimer) clearInterval(flushTimer);
                            flushTimer = null;
                            
                            messages.value[msgIndex].status = 'complete';
                            // Fallback: If the stream finished while we were disconnected, the backend sends the final content/reasoning here
                            if (event.content) messages.value[msgIndex].content = event.content;
                            if (event.reasoning) messages.value[msgIndex].reasoning = event.reasoning;
                            if (event.metadata) messages.value[msgIndex].metadata = event.metadata;
                        } else if (event.type === 'canceled') {
                            // Flush remaining tokens before applying canceled state
                            flushBuffers();
                            if (flushTimer) clearInterval(flushTimer);
                            flushTimer = null;
                            
                            messages.value[msgIndex].status = 'canceled';
                            if (event.content) messages.value[msgIndex].content = event.content;
                            if (event.reasoning) messages.value[msgIndex].reasoning = event.reasoning;
                        } else if (event.type === 'error') {
                            // Flush remaining tokens before applying error state
                            flushBuffers();
                            if (flushTimer) clearInterval(flushTimer);
                            flushTimer = null;
                            
                            messages.value[msgIndex].status = 'error';
                            if (event.content) messages.value[msgIndex].content = event.content;
                            if (event.reasoning) messages.value[msgIndex].reasoning = event.reasoning;
                            if (event.error_data) messages.value[msgIndex].error_data = event.error_data;
                        }
                    }
                }
            }
        }
        catch (error) {
            if (error instanceof Error && error.name === 'AbortError') {
                // Expected on navigation, flush whatever we have left so it matches DB
                flushBuffers();
                return;
            }
            console.error("Streaming error:", error);
        }
        finally {
            // Clean up timer and flush stragglers if loop breaks unexpectedly
            if (flushTimer) clearInterval(flushTimer);
            flushBuffers();
        }
    }

    // 5. Append a new message (used for manual edits)
    async function appendMessage(parentId: string, content: string, role: 'user' | 'assistant', attachmentIds: string[] = []): Promise<string | null> {
        try {
            const response = await apiFetch(`/api/chat/messages/${parentId}/append`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, role, attachment_ids: attachmentIds })
            });
            if (!response.ok) throw new Error('Failed to append message');
            const data = await response.json();
            
            const newMsg: Message = {
                id: data.id,
                parent_id: data.parent_id,
                role: data.role,
                content: data.content,
                reasoning: data.reasoning ?? null,
                attachments: data.attachments ?? [],
                status: data.status,
                creation_data: data.creation_data,
                error_data: data.error_data,
                metadata: data.metadata,
                created_at: data.created_at
            };
            
            messages.value.push(newMsg);
            activateLeaf(newMsg.id);

            // Bump the conversation to the top of the sidebar
            if (conversationStore.currentConversationId) {
                conversationStore.bumpLocalConversation(conversationStore.currentConversationId);
            }
            
            return newMsg.id;
        } catch (error) {
            console.error("Error appending message:", error);
            return null;
        }
    }

    // 6. Switch to a sibling branch (and descend to its most recent leaf)
    async function switchSibling(messageId: string, direction: 'prev' | 'next') {
        const { count, currentIndex } = getSiblingInfo(messageId, messages.value);
        if (count <= 1) return;

        let targetIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
        if (targetIndex < 0 || targetIndex >= count) return;

        const targetMsg = messages.value.find(m => m.id === messageId);
        if (!targetMsg || !targetMsg.parent_id) return;

        const siblings = messages.value
            .filter(m => m.parent_id === targetMsg.parent_id)
            .sort(compareMessages);
        
        const targetSibling = siblings[targetIndex];
        const targetLeafId = getMostRecentDescendantLeaf(targetSibling.id, messages.value);

        activateLeaf(targetLeafId);
        
        if (conversationStore.currentConversationId) {
            conversationStore.updateActiveLeaf(conversationStore.currentConversationId, targetLeafId);
        }
    }

    // 7. Cancel an active generation
    async function cancelGeneration() {
        if (!activeLeafId.value || !isStreaming.value) return;
        const messageId = activeLeafId.value;
        
        // Abort the local SSE listener
        stopStreaming();
        
        // Update local state immediately so UI unlocks
        const msgIndex = messages.value.findIndex(m => m.id === messageId);
        if (msgIndex !== -1) {
            messages.value[msgIndex].status = 'canceled';
        }
        
        // Tell the backend to stop the LLM and save partial content
        try {
            await apiFetch(`/api/chat/messages/${messageId}/cancel`, { method: 'POST' });
        } catch (error) {
            console.error("Error canceling message:", error);
        }
    }

    return {
        messages,
        activeLeafId,
        isStreaming,
        streamRefreshInterval,
        activePath,
        loadConversation,
        sendMessage,
        generateMessage,
        clearMessages,
        appendMessage,
        switchSibling,
        cancelGeneration
    };
});