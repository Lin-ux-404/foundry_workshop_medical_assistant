import { Fragment, type ReactNode } from "react";

interface MarkdownProps { content: string; className?: string }

function safeHref(value: string): string | null {
  try {
    const url = new URL(value);
    return ["http:", "https:", "mailto:"].includes(url.protocol) ? value : null;
  } catch {
    return null;
  }
}

function inline(source: string, depth = 0): ReactNode[] {
  if (!source || depth > 8) return [source];
  const pattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)|(\*\*|__)(.+?)\3|~~(.+?)~~|`([^`]+)`|\*([^*\n]+)\*|_([^_\n]+)_/g;
  const nodes: ReactNode[] = [];
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(source))) {
    if (match.index > last) nodes.push(source.slice(last, match.index));
    const key = `inline-${match.index}-${depth}`;
    if (match[1] !== undefined) {
      const href = safeHref(match[2]);
      nodes.push(href ? <a key={key} href={href} rel="noreferrer">{inline(match[1], depth + 1)}</a> : match[1]);
    } else if (match[4] !== undefined) {
      nodes.push(<strong key={key}>{inline(match[4], depth + 1)}</strong>);
    } else if (match[5] !== undefined) {
      nodes.push(<del key={key}>{inline(match[5], depth + 1)}</del>);
    } else if (match[6] !== undefined) {
      nodes.push(<code key={key}>{match[6]}</code>);
    } else if (match[7] !== undefined) {
      nodes.push(<em key={key}>{inline(match[7], depth + 1)}</em>);
    } else if (match[8] !== undefined) {
      nodes.push(<em key={key}>{inline(match[8], depth + 1)}</em>);
    }
    last = pattern.lastIndex;
  }
  if (last < source.length) nodes.push(source.slice(last));
  return nodes;
}

function tableCells(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split(/(?<!\\)\|/).map(cell => cell.trim().replace(/\\\|/g, "|"));
}

function isTableDivider(line: string): boolean {
  const cells = tableCells(line);
  return cells.length > 0 && cells.every(cell => /^:?-{3,}:?$/.test(cell));
}

/** Small, safe Markdown renderer for chat, orchestration messages, and task plans. */
export default function Markdown({ content, className }: MarkdownProps) {
  const lines = content.replace(/\r\n?/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let blockId = 0;

  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    const id = blockId++;
    const fence = line.match(/^\s*```([\w+-]*)\s*$/);
    if (fence) {
      const code: string[] = [];
      i++;
      while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) code.push(lines[i++]);
      if (i < lines.length) i++;
      const language = fence[1].replace(/[^\w+-]/g, "");
      blocks.push(<pre key={id}><code className={language ? `language-${language}` : undefined}>{code.join("\n")}</code></pre>);
      continue;
    }
    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (heading) {
      const Heading = `h${heading[1].length}` as "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
      blocks.push(<Heading key={id}>{inline(heading[2])}</Heading>);
      i++;
      continue;
    }
    if (/^\s{0,3}(?:[-*_]\s*){3,}$/.test(line)) { blocks.push(<hr key={id} />); i++; continue; }
    if (/^\s*>/.test(line)) {
      const quote: string[] = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) quote.push(lines[i++].replace(/^\s*> ?/, ""));
      blocks.push(<blockquote key={id}><Markdown content={quote.join("\n")} /></blockquote>);
      continue;
    }
    if (i + 1 < lines.length && line.includes("|") && isTableDivider(lines[i + 1])) {
      const headers = tableCells(line);
      const alignments = tableCells(lines[i + 1]);
      const alignmentFor = (index: number) => ({ textAlign: alignments[index]?.startsWith(":") ? alignments[index].endsWith(":") ? "center" as const : "left" as const : alignments[index]?.endsWith(":") ? "right" as const : "left" as const });
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].includes("|") && lines[i].trim()) rows.push(tableCells(lines[i++]));
      blocks.push(<div className="markdown-table-wrap" key={id}><table><thead><tr>{headers.map((cell, index) => <th key={index} style={alignmentFor(index)}>{inline(cell)}</th>)}</tr></thead><tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{headers.map((_, cellIndex) => <td key={cellIndex} style={alignmentFor(cellIndex)}>{inline(row[cellIndex] || "")}</td>)}</tr>)}</tbody></table></div>);
      continue;
    }
    const list = line.match(/^\s{0,3}([-+*]|\d+[.)])\s+(.+)$/);
    if (list) {
      const ordered = /^\d/.test(list[1]);
      const items: string[] = [];
      while (i < lines.length) {
        const item = lines[i].match(/^\s{0,3}([-+*]|\d+[.)])\s+(.+)$/);
        if (!item || /^\d/.test(item[1]) !== ordered) break;
        items.push(item[2]); i++;
      }
      const List = ordered ? "ol" : "ul";
      blocks.push(<List key={id}>{items.map((item, index) => {
        const checkbox = item.match(/^\[([ xX])\]\s*(.*)$/);
        return <li key={index}>{checkbox ? <><input type="checkbox" checked={checkbox[1].toLowerCase() === "x"} readOnly aria-label={checkbox[1].toLowerCase() === "x" ? "Complete" : "Incomplete"} />{inline(checkbox[2])}</> : inline(item)}</li>;
      })}</List>);
      continue;
    }
    const paragraph: string[] = [];
    while (i < lines.length && lines[i].trim() &&
      !/^\s{0,3}(?:#{1,6}\s|>|[-+*]\s|\d+[.)]\s|```)/.test(lines[i]) &&
      !/^\s{0,3}(?:[-*_]\s*){3,}$/.test(lines[i]) &&
      !(i + 1 < lines.length && lines[i].includes("|") && isTableDivider(lines[i + 1]))) {
      paragraph.push(lines[i++]);
    }
    if (paragraph.length) {
      blocks.push(<p key={id}>{paragraph.map((part, index) => <Fragment key={index}>{index > 0 && <br />}{inline(part)}</Fragment>)}</p>);
    } else {
      blocks.push(<p key={id}>{inline(lines[i])}</p>);
      i++;
    }
  }

  return <div className={`markdown ${className || ""}`.trim()}>{blocks}</div>;
}

