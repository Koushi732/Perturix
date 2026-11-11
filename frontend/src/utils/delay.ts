export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
export const randomLatency = (min: number, max: number) => delay(Math.floor(Math.random() * (max - min + 1) + min));
export const simulateFailure = (probability: number = 0.05) => {
  if (Math.random() < probability) {
    throw new Error("Simulated network failure. Please try again.");
  }
};
