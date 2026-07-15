// import { ref } from 'vue';
// import { Message, StreamEvent } from '../types';

// // --- Reactive State ---
// // `ref()` makes these variables reactive. When they change, Vue updates the UI.
// const messages = ref<Message[]>([]);
// const activeLeafId = ref<string | null>(null);
// const isStreaming = ref(false);

// export function useChat() {

//     // 0. Start a new conversation
//     async function createConversation(title: string | null = null, systemPrompt: string | null = null) {
//         try {
//             const response = await fetch('/api/chat/conversations', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ title, system_prompt: systemPrompt })
//             });
            
//             if (!response.ok) throw new Error('Failed to create conversation');
//             const data = await response.json();
            
//             // Initialize state with the root system message
//             activeLeafId.value = data.root_message_id;
//             messages.value = [{
//                 id: data.root_message_id,
//                 parent_id: null,
//                 role: 'system',
//                 content: systemPrompt || 'You are BOUGH, a helpful assistant.',
//                 status: 'complete',
//                 created_at: new Date().toISOString()
//             }];
//         } catch (error) {
//             console.error("Error creating conversation:", error);
//         }
//     }

//     // 1. Load an existing conversation and its history
//     async function loadConversation(conversationId: string) {
//         try {
//             const response = await fetch(`/api/chat/conversations/${conversationId}`);
//             if (!response.ok) throw new Error('Failed to load conversation');
            
//             const data = await response.json();
//             messages.value = data.messages;
//             activeLeafId.value = data.conversation.active_leaf_id;
            
//             // Check if the active message is still streaming (e.g., user refreshed page mid-stream)
//             const activeMsg = messages.value.find(m => m.id === activeLeafId.value);
//             if (activeMsg && (activeMsg.status === 'pending' || activeMsg.status === 'streaming')) {
//                 // Resume the stream
//                 startStreaming(activeMsg.id);
//             }
//         }
//         catch (error) {
//             console.error("Error loading conversation:", error);
//         }
//     }

//     // 2. User sends a new message
//     async function sendMessage(content: string) {
//         if (!activeLeafId.value || isStreaming.value) return;
        
//         try {
//             // Step A: Append the user message
//             const response = await fetch(`/api/chat/messages/${activeLeafId.value}/append`, {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ content, role: 'user' })
//             });
            
//             if (!response.ok) throw new Error('Failed to append message');
//             const data = await response.json();
//             const newMsgId = data.message_id;
            
//             // Add the new user message to our local UI state immediately
//             messages.value.push({
//                 id: newMsgId,
//                 parent_id: activeLeafId.value,
//                 role: 'user',
//                 content: content,
//                 status: 'complete',
//                 created_at: new Date().toISOString()
//             });
            
//             activeLeafId.value = newMsgId;
            
//             // Step B: Trigger generation
//             await generateMessage(newMsgId);
            
//         }
//         catch (error) {
//             console.error("Error sending message:", error);
//         }
//     }

//     // 3. Trigger LLM generation
//     async function generateMessage(parentId: string) {
//         try {
//             const response = await fetch(`/api/chat/messages/${parentId}/generate`, {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({}) // Empty body for now, uses default model
//             });
            
//             if (!response.ok) throw new Error('Failed to start generation');
//             const data = await response.json();
//             const assistantMsgId = data.message_id;
            
//             // Add a placeholder assistant message to the UI
//             messages.value.push({
//                 id: assistantMsgId,
//                 parent_id: parentId,
//                 role: 'assistant',
//                 content: '', // Starts empty
//                 status: 'pending',
//                 created_at: new Date().toISOString()
//             });
            
//             activeLeafId.value = assistantMsgId;
            
//             // Start listening to the SSE stream
//             startStreaming(assistantMsgId);
            
//         }
//         catch (error) {
//             console.error("Error generating message:", error);
//         }
//     }

//     // 4. The SSE Engine: Read the stream
//     async function startStreaming(messageId: string) {
//         isStreaming.value = true;
        
//         const response = await fetch(`/api/chat/messages/${messageId}/stream`);
        
//         if (!response.body) throw new Error('No response body');
        
//         const reader = response.body.getReader();
//         const decoder = new TextDecoder();
        
//         let buffer = '';
        
//         try {
//             while (true) {
//                 // Read bytes from the TCP stream
//                 const { done, value } = await reader.read();
                
//                 if (done) break;
                
//                 // Convert bytes to string and add to our buffer
//                 buffer += decoder.decode(value, { stream: true });
                
//                 // SSE events are separated by a double newline
//                 const chunks = buffer.split('\n\n');
                
//                 // The last item might be an incomplete chunk, so we save it back to the buffer
//                 buffer = chunks.pop() || '';
                
//                 // Process all complete chunks
//                 for (const chunk of chunks) {
//                     // Strip the "data: " prefix
//                     if (!chunk.startsWith('data: ')) continue;
//                     const jsonStr = chunk.replace('data: ', '');
                    
//                     if (jsonStr === '[DONE]') {
//                         // Stream fully finished
//                         isStreaming.value = false;
//                         return;
//                     }
                    
//                     // Parse the JSON event
//                     const event = JSON.parse(jsonStr);
                    
//                     // Find the message we are updating in the reactive array
//                     const msgIndex = messages.value.findIndex(m => m.id === messageId);
//                     if (msgIndex !== -1) {
//                         if (event.type === 'token' || event.type === 'catch_up') {
//                             // Append the token to the message content.
//                             messages.value[msgIndex].content += event.content;
//                             messages.value[msgIndex].status = 'streaming';
//                         } else if (event.type === 'done') {
//                             messages.value[msgIndex].status = 'complete';
//                             if (event.metadata) messages.value[msgIndex].metadata = event.metadata;
//                         } else if (event.type === 'error') {
//                             messages.value[msgIndex].status = 'error';
//                             if (event.error_data) messages.value[msgIndex].error_data = event.error_data;
//                         }
//                     }
//                 }
//             }
//         }
//         catch (error) {
//             console.error("Streaming error:", error);
//         }
//         finally {
//             isStreaming.value = false;
//         }
//     }

//     // Return the reactive state and functions so the UI component can use them
//     return {
//         messages,
//         activeLeafId,
//         isStreaming,
//         createConversation,
//         loadConversation,
//         sendMessage,
//         generateMessage
//     };
// }