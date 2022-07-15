import { Page } from "./Page";

export function ExportPage() {
  return (
    <Page
      title="Export Data"
      backButton={{ show: true, redirectUrl: "/" }}
    ></Page>
  );
}
