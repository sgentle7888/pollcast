<template>
  <div
    class="rich-text-editor card-glass"
    :class="{ 'is-focused': isFocused, 'is-disabled': disabled }"
  >
    <!-- Toolbar -->
    <div class="editor-toolbar" role="toolbar" aria-label="Text Formatting">
      <!-- History -->
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-btn"
          title="Undo (Ctrl+Z)"
          :disabled="disabled"
          @mousedown.prevent="execCommand('undo')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M3 7v6h6" />
            <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
          </svg>
        </button>
        <button
          type="button"
          class="toolbar-btn"
          title="Redo (Ctrl+Y)"
          :disabled="disabled"
          @mousedown.prevent="execCommand('redo')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21 7v6h-6" />
            <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7" />
          </svg>
        </button>
      </div>

      <div class="toolbar-sep"></div>

      <!-- Text Styles -->
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-btn text-bold"
          :class="{ active: activeStates.bold }"
          title="Bold (Ctrl+B)"
          :disabled="disabled"
          @mousedown.prevent="execCommand('bold')"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          class="toolbar-btn text-italic"
          :class="{ active: activeStates.italic }"
          title="Italic (Ctrl+I)"
          :disabled="disabled"
          @mousedown.prevent="execCommand('italic')"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          class="toolbar-btn text-underline"
          :class="{ active: activeStates.underline }"
          title="Underline (Ctrl+U)"
          :disabled="disabled"
          @mousedown.prevent="execCommand('underline')"
        >
          <u>U</u>
        </button>
        <button
          type="button"
          class="toolbar-btn text-strike"
          :class="{ active: activeStates.strikeThrough }"
          title="Strikethrough"
          :disabled="disabled"
          @mousedown.prevent="execCommand('strikeThrough')"
        >
          <s>S</s>
        </button>
      </div>

      <div class="toolbar-sep"></div>

      <!-- Headings / Blocks -->
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-btn text-btn"
          :class="{ active: activeStates.h2 }"
          title="Heading 2"
          :disabled="disabled"
          @mousedown.prevent="toggleBlock('h2')"
        >
          H2
        </button>
        <button
          type="button"
          class="toolbar-btn text-btn"
          :class="{ active: activeStates.h3 }"
          title="Heading 3"
          :disabled="disabled"
          @mousedown.prevent="toggleBlock('h3')"
        >
          H3
        </button>
        <button
          type="button"
          class="toolbar-btn text-btn"
          :class="{ active: activeStates.p }"
          title="Normal Paragraph"
          :disabled="disabled"
          @mousedown.prevent="toggleBlock('p')"
        >
          ¶
        </button>
      </div>

      <div class="toolbar-sep"></div>

      <!-- Lists & Quotes -->
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-btn"
          :class="{ active: activeStates.unorderedList }"
          title="Bulleted List"
          :disabled="disabled"
          @mousedown.prevent="execCommand('insertUnorderedList')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <line x1="3" y1="6" x2="3.01" y2="6" />
            <line x1="3" y1="12" x2="3.01" y2="12" />
            <line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
        </button>
        <button
          type="button"
          class="toolbar-btn"
          :class="{ active: activeStates.orderedList }"
          title="Numbered List"
          :disabled="disabled"
          @mousedown.prevent="execCommand('insertOrderedList')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="10" y1="6" x2="21" y2="6" />
            <line x1="10" y1="12" x2="21" y2="12" />
            <line x1="10" y1="18" x2="21" y2="18" />
            <path d="M4 6h1v4" />
            <path d="M4 10h2" />
            <path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1" />
          </svg>
        </button>
        <button
          type="button"
          class="toolbar-btn"
          :class="{ active: activeStates.blockquote }"
          title="Quote Block"
          :disabled="disabled"
          @mousedown.prevent="toggleBlock('blockquote')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M3 21c3 0 7-1 7-8V5c0-1.25-.75-2-2-2H4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 1-1 2 1 2 2 2z"
            />
            <path
              d="M15 21c3 0 7-1 7-8V5c0-1.25-.75-2-2-2h-4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 1-1 2 1 2 2 2z"
            />
          </svg>
        </button>
      </div>

      <div class="toolbar-sep"></div>

      <!-- Links & Clean -->
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-btn"
          :class="{ active: activeStates.link || showLinkPopover }"
          title="Insert / Edit Link"
          :disabled="disabled"
          @mousedown.prevent="toggleLinkPopover"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"
            />
            <path
              d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
            />
          </svg>
        </button>
        <button
          v-if="activeStates.link"
          type="button"
          class="toolbar-btn text-danger"
          title="Remove Link"
          :disabled="disabled"
          @mousedown.prevent="execCommand('unlink')"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m18.84 12.25 1.72-1.71a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="m5.16 11.75-1.71 1.72a5 5 0 0 0 7.07 7.07l1.71-1.72" />
            <line x1="2" y1="2" x2="22" y2="22" />
          </svg>
        </button>
        <button
          type="button"
          class="toolbar-btn text-muted-btn"
          title="Clear Formatting"
          :disabled="disabled"
          @mousedown.prevent="clearFormatting"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"
            />
            <path d="M22 21H7" />
            <path d="m5 11 9 9" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Inline Link Popover -->
    <div
      v-if="showLinkPopover"
      class="link-popover card-glass animate-fade-in-up"
      @mousedown.stop
    >
      <div class="link-popover-row">
        <input
          ref="linkInputRef"
          v-model="linkUrl"
          type="url"
          class="form-control form-control-sm link-input"
          placeholder="https://example.com"
          @keydown.enter.prevent="applyLink"
          @keydown.esc.prevent="closeLinkPopover"
        />
        <button type="button" class="btn btn-primary btn-sm" @click="applyLink">
          Apply
        </button>
        <button
          type="button"
          class="btn btn-ghost btn-sm"
          @click="closeLinkPopover"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Editable Area -->
    <div
      ref="editorRef"
      class="editor-content"
      :contenteditable="!disabled"
      :data-placeholder="placeholder"
      role="textbox"
      aria-multiline="true"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keyup="updateActiveStates"
      @mouseup="updateActiveStates"
      @selectionchange="updateActiveStates"
    ></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from "vue";
import DOMPurify from "dompurify";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default: "Optional context or instructions for participants…",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "focus", "blur"]);

const editorRef = ref(null);
const linkInputRef = ref(null);
const isFocused = ref(false);
const showLinkPopover = ref(false);
const linkUrl = ref("");
let savedSelectionRange = null;

const activeStates = reactive({
  bold: false,
  italic: false,
  underline: false,
  strikeThrough: false,
  unorderedList: false,
  orderedList: false,
  h2: false,
  h3: false,
  p: false,
  blockquote: false,
  link: false,
});

// Configure DOMPurify to allow standard formatting tags & attributes
const purifyConfig = {
  ALLOWED_TAGS: [
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "strike",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "a",
    "span",
    "div",
  ],
  ALLOWED_ATTR: ["href", "target", "rel", "class", "style"],
};

const sanitizeHtml = (html) => {
  if (!html) return "";
  return DOMPurify.sanitize(html, purifyConfig);
};

const isEditorEmpty = (html) => {
  if (!html) return true;
  const stripped = html
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .trim();
  return stripped.length === 0;
};

// Sync internal editor content with incoming modelValue
const setEditorContent = (val) => {
  if (!editorRef.value) return;
  const clean = sanitizeHtml(val || "");
  if (editorRef.value.innerHTML !== clean) {
    editorRef.value.innerHTML = clean;
  }
};

watch(
  () => props.modelValue,
  (newVal) => {
    if (!editorRef.value) return;
    const currentHtml = editorRef.value.innerHTML;
    const cleanNew = sanitizeHtml(newVal || "");
    // Only update DOM if the rendered HTML actually differs
    if (
      cleanNew !== currentHtml &&
      (isEditorEmpty(cleanNew) !== isEditorEmpty(currentHtml) ||
        cleanNew !== sanitizeHtml(currentHtml))
    ) {
      setEditorContent(cleanNew);
    }
  },
);

onMounted(() => {
  setEditorContent(props.modelValue);
});

const onInput = () => {
  if (!editorRef.value) return;
  const rawHtml = editorRef.value.innerHTML;
  if (isEditorEmpty(rawHtml)) {
    emit("update:modelValue", "");
  } else {
    emit("update:modelValue", sanitizeHtml(rawHtml));
  }
  updateActiveStates();
};

const onFocus = (e) => {
  isFocused.value = true;
  emit("focus", e);
};

const onBlur = (e) => {
  isFocused.value = false;
  emit("blur", e);
};

// Check active formatting for toolbar feedback
const updateActiveStates = () => {
  if (typeof document === "undefined") return;

  try {
    activeStates.bold = document.queryCommandState("bold");
    activeStates.italic = document.queryCommandState("italic");
    activeStates.underline = document.queryCommandState("underline");
    activeStates.strikeThrough = document.queryCommandState("strikeThrough");
    activeStates.unorderedList = document.queryCommandState(
      "insertUnorderedList",
    );
    activeStates.orderedList = document.queryCommandState("insertOrderedList");

    const sel = window.getSelection();
    if (sel && sel.rangeCount > 0 && editorRef.value) {
      let node = sel.getRangeAt(0).commonAncestorContainer;
      if (node.nodeType === 3) node = node.parentNode;

      let inH2 = false;
      let inH3 = false;
      let inBlockquote = false;
      let inLink = false;
      let inP = false;

      let cur = node;
      while (cur && cur !== editorRef.value) {
        const tag = cur.tagName ? cur.tagName.toLowerCase() : "";
        if (tag === "h2") inH2 = true;
        if (tag === "h3") inH3 = true;
        if (tag === "blockquote") inBlockquote = true;
        if (tag === "a") inLink = true;
        if (tag === "p") inP = true;
        cur = cur.parentNode;
      }

      activeStates.h2 = inH2;
      activeStates.h3 = inH3;
      activeStates.blockquote = inBlockquote;
      activeStates.link = inLink;
      activeStates.p = inP;
    }
  } catch {
    // Ignore queryCommandState quirks on edge cases
  }
};

const execCommand = (cmd, val = null) => {
  if (props.disabled || !editorRef.value) return;
  editorRef.value.focus();
  document.execCommand(cmd, false, val);
  onInput();
};

const toggleBlock = (tag) => {
  if (props.disabled || !editorRef.value) return;
  editorRef.value.focus();
  const currentVal = (
    document.queryCommandValue("formatBlock") || ""
  ).toLowerCase();
  if (currentVal.includes(tag)) {
    document.execCommand("formatBlock", false, "<p>");
  } else {
    document.execCommand("formatBlock", false, `<${tag}>`);
  }
  onInput();
};

const clearFormatting = () => {
  if (props.disabled || !editorRef.value) return;
  editorRef.value.focus();
  document.execCommand("removeFormat", false, null);
  document.execCommand("formatBlock", false, "<p>");
  onInput();
};

// Link Popover handling
const saveSelection = () => {
  const sel = window.getSelection();
  if (sel && sel.rangeCount > 0) {
    savedSelectionRange = sel.getRangeAt(0).cloneRange();
  }
};

const restoreSelection = () => {
  if (savedSelectionRange) {
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(savedSelectionRange);
  }
};

const toggleLinkPopover = () => {
  if (showLinkPopover.value) {
    closeLinkPopover();
    return;
  }
  saveSelection();
  showLinkPopover.value = true;
  linkUrl.value = "";
  // Check if cursor is already on an <a> element
  const sel = window.getSelection();
  if (sel && sel.rangeCount > 0) {
    let node = sel.getRangeAt(0).commonAncestorContainer;
    if (node.nodeType === 3) node = node.parentNode;
    let cur = node;
    while (cur && cur !== editorRef.value) {
      if (cur.tagName && cur.tagName.toLowerCase() === "a") {
        linkUrl.value = cur.getAttribute("href") || "";
        break;
      }
      cur = cur.parentNode;
    }
  }
  nextTick(() => {
    linkInputRef.value?.focus();
    linkInputRef.value?.select();
  });
};

const closeLinkPopover = () => {
  showLinkPopover.value = false;
  linkUrl.value = "";
  savedSelectionRange = null;
};

const applyLink = () => {
  const raw = linkUrl.value.trim();
  if (!raw) {
    closeLinkPopover();
    return;
  }

  let safeUrl = raw;
  if (!/^(https?:\/\/|mailto:)/i.test(safeUrl)) {
    closeLinkPopover();
    return;
  }

  restoreSelection();
  execCommand("createLink", safeUrl);

  // Set target="_blank" and rel="noopener noreferrer" on new links
  if (editorRef.value) {
    editorRef.value.querySelectorAll("a").forEach((a) => {
      if (!a.getAttribute("target")) {
        a.setAttribute("target", "_blank");
        a.setAttribute("rel", "noopener noreferrer");
      }
    });
  }

  onInput();
  closeLinkPopover();
};
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  border-radius: var(--r-md);
  border: 1px solid var(--border);
  background: var(--bg-input);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.rich-text-editor.is-focused {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.rich-text-editor.is-disabled {
  opacity: 0.65;
  pointer-events: none;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  padding: 0.4rem 0.5rem;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  user-select: none;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.toolbar-sep {
  width: 1px;
  height: 18px;
  background: var(--border);
  margin: 0 4px;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  border-radius: var(--r-xs);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--glass-hover);
  color: var(--text-primary);
}

.toolbar-btn.active {
  background: var(--accent-dim);
  color: var(--accent);
  border-color: var(--border-accent);
}

.toolbar-btn.text-bold {
  font-weight: 800;
}

.toolbar-btn.text-btn {
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

.toolbar-btn.text-danger:hover {
  color: var(--danger);
  background: var(--danger-dim);
}

/* Link Popover */
.link-popover {
  position: absolute;
  top: 44px;
  left: 12px;
  right: 12px;
  z-index: 20;
  padding: 0.6rem;
  border-radius: var(--r-md);
  border: 1px solid var(--border-focus);
  background: var(--bg-surface);
  box-shadow: var(--shadow-lg);
}

.link-popover-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.link-input {
  flex: 1;
}

/* Contenteditable Area */
.editor-content {
  min-height: 110px;
  max-height: 360px;
  overflow-y: auto;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.6;
  outline: none;
}

/* Placeholder */
.editor-content:empty:before {
  content: attr(data-placeholder);
  color: var(--text-muted);
  pointer-events: none;
  font-style: normal;
  display: block;
}

/* Typography styles inside editor */
.editor-content :deep(p) {
  margin: 0 0 0.5rem 0;
}

.editor-content :deep(p:last-child) {
  margin-bottom: 0;
}

.editor-content :deep(h2) {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0.75rem 0 0.4rem 0;
  line-height: 1.3;
}

.editor-content :deep(h3) {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0.6rem 0 0.3rem 0;
  line-height: 1.35;
}

.editor-content :deep(ul),
.editor-content :deep(ol) {
  margin: 0.4rem 0 0.6rem 1.5rem;
  padding: 0;
}

.editor-content :deep(li) {
  margin-bottom: 0.25rem;
}

.editor-content :deep(blockquote) {
  margin: 0.6rem 0;
  padding: 0.4rem 0.8rem;
  border-left: 3px solid var(--accent);
  background: var(--glass-hover);
  border-radius: 0 var(--r-xs) var(--r-xs) 0;
  color: var(--text-secondary);
  font-style: italic;
}

.editor-content :deep(a) {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.editor-content :deep(strong) {
  font-weight: 700;
  color: var(--text-primary);
}

.editor-content :deep(em) {
  font-style: italic;
}

.editor-content :deep(u) {
  text-decoration: underline;
}

.editor-content :deep(s),
.editor-content :deep(strike) {
  text-decoration: line-through;
  opacity: 0.8;
}
</style>
