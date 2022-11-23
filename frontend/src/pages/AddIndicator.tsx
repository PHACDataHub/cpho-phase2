import IndicatorForm from "./components/addIndicatorForm/IndicatorForm";
import { Page } from "./Page";

export function AddIndicator() {
  return (
    <Page backButton={{ show: true, redirectUrl: "/" }} title="Add Indicator">
      <IndicatorForm />
    </Page>
  );
}
