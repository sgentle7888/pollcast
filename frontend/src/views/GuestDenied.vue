<template>
  <div class="guest-denied">
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="lock-icon"
    >
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
    <h2>Access Restricted</h2>
    <p>
      This page requires you to be logged in. If you have a poll or survey link,
      please open the full link directly (it should end with
      <code>#/surveys/...</code> or <code>#/polls/...</code>).
    </p>
    <a href="/login" class="signin">Sign In</a>
  </div>
</template>

<style scoped>
.guest-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 2rem;
  gap: 1rem;
}
.lock-icon {
  color: var(--text-muted);
}
h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}
p {
  color: var(--text-secondary);
  max-width: 340px;
  line-height: 1.6;
}
.signin {
  margin-top: 0.5rem;
  padding: 0.6rem 1.5rem;
  background: var(--accent);
  color: #fff;
  border-radius: var(--r-md);
  font-weight: 600;
  text-decoration: none;
}
</style>
