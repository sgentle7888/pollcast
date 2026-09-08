<template>
  <div class="modal-overlay animate-fade-in" @click.self="$emit('close')">
    <div class="modal card-glass branding-modal animate-scale-up" role="dialog" aria-modal="true">

      <!-- Header -->
      <div class="modal-header">
        <div class="header-left">
          <div class="modal-icon-badge">
            <AppIcons name="settings" size="20" />
          </div>
          <div>
            <h3 class="modal-title">Company Branding</h3>
            <p class="modal-subtitle">Upload your company logo to display on every survey interface.</p>
          </div>
        </div>
        <button class="btn btn-ghost btn-icon close-btn" @click="$emit('close')" title="Close">
          <AppIcons name="x" size="18" />
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">

        <!-- Current Logo Card -->
        <div class="current-logo-card card">
          <div class="section-label-row">
            <span class="label-text">Current Active Logo</span>
            <span v-if="auth.companyLogo" class="badge badge-success">
              <span class="pulse-dot"></span> Active
            </span>
            <span v-else class="badge badge-neutral">Not Configured</span>
          </div>

          <div class="logo-preview-box" :class="{ 'has-logo': !!auth.companyLogo }">
            <template v-if="auth.companyLogo">
              <img :src="auth.companyLogo" alt="Company Logo" class="preview-img" />
            </template>
            <div v-else class="empty-logo-placeholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="placeholder-icon">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span>No custom logo uploaded yet</span>
              <span class="text-xs text-muted">Default system branding is currently used</span>
            </div>
          </div>

          <div v-if="auth.companyLogo" class="current-actions">
            <button
              class="btn btn-ghost btn-sm text-danger"
              :disabled="removing"
              @click="removeLogo"
            >
              <AppIcons name="trash" size="14" />
              <span>{{ removing ? 'Removing…' : 'Remove Logo' }}</span>
            </button>
          </div>
        </div>

        <!-- Upload Dropzone -->
        <div
          class="dropzone-area card-interactive"
          :class="{ 'is-dragging': isDragging, 'has-selected': !!selectedFile }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/svg+xml, image/webp"
            style="display: none;"
            @change="onFileChanged"
          />

          <!-- If file selected for upload -->
          <div v-if="selectedFile" class="selected-file-view" @click.stop>
            <div class="selected-preview-wrap">
              <img v-if="selectedPreviewUrl" :src="selectedPreviewUrl" alt="New Logo Preview" class="selected-preview-img" />
            </div>
            <div class="selected-file-meta">
              <div class="selected-filename">{{ selectedFile.name }}</div>
              <div class="selected-filesize">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
            <button class="btn btn-ghost btn-icon btn-sm clear-file-btn" @click="clearSelectedFile" title="Cancel selection">
              <AppIcons name="x" size="14" />
            </button>
          </div>

          <!-- Default Dropzone Prompt -->
          <div v-else class="dropzone-prompt">
            <div class="upload-icon-circle">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <div class="prompt-text">
              <span class="prompt-bold">Click to upload</span> or drag and drop logo here
            </div>
            <div class="prompt-subtext">
              PNG, JPG, SVG, or WEBP up to 5MB (Transparent PNG or SVG recommended)
            </div>
          </div>
        </div>

        <!-- Helper hint -->
        <div class="branding-notice">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="notice-icon">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>Once uploaded, this logo will instantly appear at the top of <strong>every Take Survey interface</strong> and survey reports for respondents.</span>
        </div>

      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
        <button
          class="btn btn-primary"
          :disabled="!selectedFile || uploading"
          @click="uploadLogo"
        >
          <span v-if="uploading" class="spinner spinner-sm"></span>
          <span v-else>Upload & Apply Logo</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, inject } from "vue";
import { useAuthStore } from "../stores/auth.js";
import { frappeUpload, frappeCall } from "../api/frappe.js";
import AppIcons from "./AppIcons.vue";

const emit = defineEmits(["close", "saved"]);
const auth = useAuthStore();
const toast = inject("toast");

const fileInputRef = ref(null);
const selectedFile = ref(null);
const selectedPreviewUrl = ref(null);
const isDragging = ref(false);
const uploading = ref(false);
const removing = ref(false);

const allowedExtensions = [".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"];
const maxSizeBytes = 5 * 1024 * 1024; // 5 MB

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const validateFile = (file) => {
  if (!file) return false;
  const ext = "." + file.name.split(".").pop().toLowerCase();
  if (!allowedExtensions.includes(ext)) {
    toast?.("Invalid file format. Please upload PNG, JPG, SVG, or WEBP.", "error");
    return false;
  }
  if (file.size > maxSizeBytes) {
    toast?.("File size exceeds 5MB limit. Please choose a smaller image.", "error");
    return false;
  }
  return true;
};

const handleSelectedFile = (file) => {
  if (!validateFile(file)) return;
  selectedFile.value = file;
  if (selectedPreviewUrl.value) {
    URL.revokeObjectURL(selectedPreviewUrl.value);
  }
  selectedPreviewUrl.value = URL.createObjectURL(file);
};

const onFileChanged = (e) => {
  const file = e.target.files?.[0];
  if (file) handleSelectedFile(file);
};

const onDrop = (e) => {
  isDragging.value = false;
  const file = e.dataTransfer.files?.[0];
  if (file) handleSelectedFile(file);
};

const clearSelectedFile = () => {
  if (selectedPreviewUrl.value) {
    URL.revokeObjectURL(selectedPreviewUrl.value);
    selectedPreviewUrl.value = null;
  }
  selectedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = "";
};

const formatFileSize = (bytes) => {
  if (!bytes) return "0 B";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
};

const uploadLogo = async () => {
  if (!selectedFile.value) return;
  uploading.value = true;
  try {
    const result = await frappeUpload("pollcast.api.upload_company_logo", selectedFile.value);
    if (result?.logo) {
      auth.setCompanyLogo(result.logo);
      toast?.("Company logo updated successfully! It will now appear on all survey interfaces.", "success");
      clearSelectedFile();
      emit("saved", result.logo);
      emit("close");
    } else if (result?.error) {
      toast?.(result.error, "error");
    }
  } catch (err) {
    toast?.(err.message || "Failed to upload logo", "error");
  } finally {
    uploading.value = false;
  }
};

const removeLogo = async () => {
  if (!confirm("Are you sure you want to remove the custom company logo?")) return;
  removing.value = true;
  try {
    const res = await frappeCall("pollcast.api.remove_company_logo");
    auth.setCompanyLogo(res?.logo || "");
    toast?.("Custom logo removed. Default branding restored.", "info");
    emit("saved", res?.logo || "");
  } catch (err) {
    toast?.(err.message || "Failed to remove logo", "error");
  } finally {
    removing.value = false;
  }
};
</script>

<style scoped>
.branding-modal {
  max-width: 540px;
  width: 100%;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: var(--bg-elevated);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-lg), 0 0 32px var(--accent-glow);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.modal-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: var(--r-md);
  background: var(--accent-dim);
  color: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.close-btn {
  color: var(--text-muted);
}
.close-btn:hover {
  color: var(--text-primary);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Current Logo */
.current-logo-card {
  padding: 1.125rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.label-text {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.logo-preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 90px;
  padding: 1rem;
  border-radius: var(--r-sm);
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed var(--glass-border);
}

:root[data-theme="light"] .logo-preview-box {
  background: rgba(0, 0, 0, 0.03);
}

.preview-img {
  max-height: 64px;
  max-width: 220px;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.15));
}

.empty-logo-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.8125rem;
  text-align: center;
}

.placeholder-icon {
  opacity: 0.5;
}

.current-actions {
  display: flex;
  justify-content: flex-end;
}

/* Dropzone */
.dropzone-area {
  border: 2px dashed var(--glass-border);
  border-radius: var(--r-lg);
  padding: 1.5rem 1rem;
  text-align: center;
  cursor: pointer;
  background: var(--glass-bg);
  transition: all var(--dur) var(--ease);
}

.dropzone-area:hover,
.dropzone-area.is-dragging {
  border-color: var(--accent);
  background: var(--accent-dim);
  transform: translateY(-2px);
}

.dropzone-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.25rem;
}

.prompt-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.prompt-bold {
  color: var(--accent-light);
  font-weight: 600;
}

.prompt-subtext {
  font-size: 0.725rem;
  color: var(--text-muted);
}

/* Selected File Preview */
.selected-file-view {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  text-align: left;
}

.selected-preview-wrap {
  width: 60px;
  height: 60px;
  border-radius: var(--r-sm);
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  flex-shrink: 0;
}

.selected-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.selected-file-meta {
  flex: 1;
  min-width: 0;
}

.selected-filename {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-filesize {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

/* Notice */
.branding-notice {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: var(--r-md);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  font-size: 0.775rem;
  color: var(--text-secondary);
  line-height: 1.45;
}

.notice-icon {
  color: var(--accent-light);
  margin-top: 0.1rem;
  flex-shrink: 0;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}

.animate-scale-up {
  animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
