import { InstrumentDetailPage } from "./instrument-detail-client";

export function generateStaticParams() {
  return [{ id: "0" }];
}

export default function Page() {
  return <InstrumentDetailPage />;
}
