export type ValidationResult = string | null;

export const validators = {
  required: (value: any, fieldName: string = 'This field'): ValidationResult => {
    if (value === null || value === undefined || value === '') {
      return `${fieldName} is required`;
    }
    return null;
  },
  
  min: (value: number, min: number, fieldName: string = 'Value'): ValidationResult => {
    if (value < min) {
      return `${fieldName} must be at least ${min}`;
    }
    return null;
  },

  max: (value: number, max: number, fieldName: string = 'Value'): ValidationResult => {
    if (value > max) {
      return `${fieldName} must be at most ${max}`;
    }
    return null;
  },

  range: (value: number, min: number, max: number, fieldName: string = 'Value'): ValidationResult => {
    if (value < min || value > max) {
      return `${fieldName} must be between ${min} and ${max}`;
    }
    return null;
  },

  isImage: (file: File | null): ValidationResult => {
    if (!file) return 'File is required';
    if (!file.type.startsWith('image/')) {
      return 'Please upload a valid image file (JPEG, PNG, etc).';
    }
    if (file.size > 10 * 1024 * 1024) {
      return 'Image size must be less than 10MB';
    }
    return null;
  }
};

export function validateAll(validations: ValidationResult[]): string[] {
  return validations.filter((v): v is string => v !== null);
}
