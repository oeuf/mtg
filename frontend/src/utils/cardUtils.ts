const KNOWN_TYPES = ['Creature', 'Planeswalker', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land'] as const;

export function extractPrimaryType(typeLine: string): string {
  const typesPart = typeLine.split(' — ')[0];
  for (const t of KNOWN_TYPES) {
    if (typesPart.includes(t)) return t;
  }
  return 'Other';
}
