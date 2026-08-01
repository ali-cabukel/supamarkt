export function parseInstrumentDetailPath(pathname: string): number | null {
  const match = pathname.match(/^\/instruments\/(\d+)\/?$/);
  if (!match) return null;

  const instrumentId = Number(match[1]);
  return Number.isNaN(instrumentId) ? null : instrumentId;
}

export function resolveInstrumentId(pathname: string, paramId: string): number | null {
  if (typeof window !== "undefined") {
    const fromWindow = parseInstrumentDetailPath(window.location.pathname);
    if (fromWindow !== null) return fromWindow;
  }

  const fromPath = parseInstrumentDetailPath(pathname);
  if (fromPath !== null) return fromPath;

  const fromParam = Number(paramId);
  return Number.isNaN(fromParam) ? null : fromParam;
}
