export default function highlight(line: string, query: string) {
  if (!query) return line;
  const regex = new RegExp(`(${query})`, 'gi');
  return line.replace(regex, '<mark class="bg-yellow-200 text-black">$1</mark>')
}