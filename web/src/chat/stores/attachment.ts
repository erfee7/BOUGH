import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { AttachmentDraft } from '@/types';
import { apiFetch } from '@/utils/api';

// Mirrors of backend caps (routers/attachments.py MAX_ATTACHMENT_SIZE,
// routers/messages.py MAX_MESSAGE_ATTACHMENTS). Personal scale, no config endpoint —
// keep in sync when the backend constants change.
const MAX_FILE_SIZE = 25 * 1024 * 1024;
const MAX_DRAFTS = 8;
const ALLOWED_MIME_TYPES = new Set([
    'image/png', 'image/jpeg', 'image/webp', 'image/gif', 'application/pdf'
]);

let localIdCounter = 0;

export const useAttachmentStore = defineStore('attachment', () => {
    const drafts = ref<AttachmentDraft[]>([]);

    // --- Getters ---
    const readyAttachmentIds = computed(() =>
        drafts.value.filter(d => d.status === 'done' && d.meta).map(d => d.meta!.id)
    );
    const isUploading = computed(() => drafts.value.some(d => d.status === 'uploading'));
    const hasBlockingDrafts = computed(() =>
        drafts.value.some(d => d.status === 'uploading' || d.status === 'error')
    );

    // --- Actions ---

    async function uploadDraft(localId: string) {
        const draft = drafts.value.find(d => d.localId === localId);
        if (!draft || draft.status !== 'uploading') return;

        // Never set Content-Type manually: the browser must generate the multipart boundary.
        const formData = new FormData();
        formData.append('file', draft.file);

        try {
            const response = await apiFetch('/api/chat/attachments', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let detail = `Upload failed (${response.status})`;
                try {
                    const data = await response.json();
                    if (data?.detail) detail = data.detail;
                } catch { /* non-JSON body; keep the default */ }
                const target = drafts.value.find(d => d.localId === localId);
                if (target) {
                    target.status = 'error';
                    target.error = detail;
                }
                return;
            }

            const data = await response.json();
            // Re-resolve: the draft may have been removed while the request was in flight
            const target = drafts.value.find(d => d.localId === localId);
            if (!target) return; // Discarded — the orphaned blob is purged server-side within 24h

            // Typed API boundary: construct explicitly from raw JSON
            target.meta = {
                id: String(data.id),
                mime_type: String(data.mime_type),
                filename: String(data.filename),
                size: Number(data.size)
            };
            target.status = 'done';
        } catch (error) {
            // Network-level failure (includes the thrown 401 session-expiry interception)
            const target = drafts.value.find(d => d.localId === localId);
            if (target) {
                target.status = 'error';
                target.error = error instanceof Error ? error.message : 'Upload failed';
            }
        }
    }

    function addFiles(files: File[]) {
        for (const file of files) {
            if (drafts.value.length >= MAX_DRAFTS) {
                console.warn('Attachment draft cap reached; ignoring further files.');
                break;
            }
            const localId = `att-${Date.now()}-${localIdCounter++}`;

            // Client fast-fail pre-checks (UX only; the server's magic-number check remains the authority)
            if (file.size > MAX_FILE_SIZE) {
                drafts.value.push({
                    localId, file, status: 'error',
                    error: `File exceeds ${MAX_FILE_SIZE / (1024 * 1024)} MB`
                });
                continue;
            }
            if (!ALLOWED_MIME_TYPES.has(file.type)) {
                drafts.value.push({ localId, file, status: 'error', error: 'Unsupported file type' });
                continue;
            }

            drafts.value.push({ localId, file, status: 'uploading' });
            void uploadDraft(localId);
        }
    }

    function removeDraft(localId: string) {
        drafts.value = drafts.value.filter(d => d.localId !== localId);
    }

    function retryDraft(localId: string) {
        const draft = drafts.value.find(d => d.localId === localId);
        if (!draft || draft.status !== 'error') return;
        draft.status = 'uploading';
        draft.error = undefined;
        void uploadDraft(localId);
    }

    function clearDrafts() {
        drafts.value = [];
    }

    return {
        drafts,
        readyAttachmentIds,
        isUploading,
        hasBlockingDrafts,
        addFiles,
        removeDraft,
        retryDraft,
        clearDrafts
    };
});