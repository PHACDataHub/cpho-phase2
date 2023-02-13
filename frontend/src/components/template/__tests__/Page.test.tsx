import { screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { render } from "../../../test-utils";
import { Page } from "../Page";

const mockNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"), // use actual for all non-hook parts
  useNavigate: () => mockNavigate,
}));

describe("Page", () => {
  test("Renders page template without button if not prompt", () => {
    const { getByRole, getByText } = render(
      <BrowserRouter>
        <Page title="Test Title">
          <p>Test</p>
        </Page>
      </BrowserRouter>
    );

    const title = screen.getByText(/Test Title/i);

    expect(title).toBeInTheDocument();

    expect(getByRole("heading")).toHaveTextContent("Test Title");
    expect(getByText("Test")).toBeInTheDocument();
  });

  test("Renders page template with button if prompt", () => {
    const { getByRole, getByText } = render(
      <BrowserRouter>
        <Page
          title="Test Title"
          backButton={{ show: true, redirectUrl: "/test" }}
        >
          <p>Test</p>
        </Page>
      </BrowserRouter>
    );

    const title = screen.getByText(/Test Title/i);

    expect(title).toBeInTheDocument();

    expect(getByRole("heading")).toHaveTextContent("Test Title");
    expect(getByText("Test")).toBeInTheDocument();
    expect(getByText("Back")).toBeInTheDocument();
  });

  test("Calls navigate to specified path if back button is clicked", () => {
    const { getByText } = render(
      <BrowserRouter>
        <Page
          title="Test Title"
          backButton={{ show: true, redirectUrl: "/test" }}
        >
          <p>Test</p>
        </Page>
      </BrowserRouter>
    );

    const backButton = getByText("Back");

    expect(backButton).toBeInTheDocument();

    backButton.click();

    expect(mockNavigate).toHaveBeenCalledWith("/test");
  });
});
