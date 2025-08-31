export default function scrollToLine(lineNumber: number, page_size: number): void {
    const element = document.getElementById(`line-${lineNumber % page_size}`);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}