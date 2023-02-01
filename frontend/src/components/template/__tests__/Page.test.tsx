import { screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { render } from "../../../test-utils";
import { Page } from "../Page";

test("Renders page template", () => {
  render(
    <BrowserRouter>
      <Page title="Test Title">
        <div>Test</div>
      </Page>
    </BrowserRouter>
  );

  const title = screen.getByText(/Test Title/i);

  expect(title).toBeInTheDocument();
});
