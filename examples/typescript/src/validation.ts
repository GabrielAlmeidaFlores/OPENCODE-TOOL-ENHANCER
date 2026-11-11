export interface CreateUserInput {
  email?: unknown;
  name?: unknown;
  age?: unknown;
}

export interface ValidationResult {
  ok: boolean;
  errors: string[];
}

export function validateCreateUser(input: CreateUserInput): ValidationResult {
  const errors: string[] = [];

  if (typeof input.email !== "string" || !input.email.includes("@")) {
    errors.push("email must be a valid address");
  }

  if (typeof input.name !== "string" || input.name.trim().length === 0) {
    errors.push("name is required");
  }

  if (input.age !== undefined) {
    if (typeof input.age !== "number" || !Number.isInteger(input.age) || input.age < 0) {
      errors.push("age must be a non-negative integer");
    }
  }

  return { ok: errors.length === 0, errors };
}
