let elapsedTypingTime: number = 0;
let entries: number = 0;

export function isVirtual(): boolean {
  return entries != 0 ? elapsedTypingTime / entries <= 25 : false;
}

export function addEntry(time: number): void {
  elapsedTypingTime += time;
  entries++;
}

export function reset(): void {
  elapsedTypingTime = 0;
  entries = 0;
}