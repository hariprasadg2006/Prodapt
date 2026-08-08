// Frontend-only validation helpers.
// No network calls, no backend — purely local checks on form state.

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(value) {
  return EMAIL_PATTERN.test(value.trim());
}

export function isValidPassword(value) {
  return value.length >= 8;
}

export function validateSignUp({ name, email, password }) {
  const errors = {};

  if (!name.trim()) {
    errors.name = "Enter your full name.";
  }

  if (!email.trim()) {
    errors.email = "Enter your email address.";
  } else if (!isValidEmail(email)) {
    errors.email = "Enter a valid email address.";
  }

  if (!password) {
    errors.password = "Create a password.";
  } else if (!isValidPassword(password)) {
    errors.password = "Password needs at least 8 characters.";
  }

  return errors;
}

export function validateSignIn({ email, password }) {
  const errors = {};

  if (!email.trim()) {
    errors.email = "Enter your email address.";
  } else if (!isValidEmail(email)) {
    errors.email = "Enter a valid email address.";
  }

  if (!password) {
    errors.password = "Enter your password.";
  }

  return errors;
}
