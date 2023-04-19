import IndicatorForm from "../organisms/IndicatorForm";
import { Page } from "../template/Page";

export function AddIndicator() {
  return (
    <Page backButton={{ show: true, redirectUrl: "/" }} title="Add Data">
      <IndicatorForm mode="create" />
    </Page>
  );
}
