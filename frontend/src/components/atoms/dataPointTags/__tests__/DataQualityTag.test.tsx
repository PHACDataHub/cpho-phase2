import { screen } from "@testing-library/react";
import { render } from "../../../../test-utils";
import DataQualityTag from "../DataQualityTag";
import "@testing-library/jest-dom";

const mockSetDataQuality = jest.fn();

describe("DataQualityTag", () => {
  it("should show Not Selected if dataQuality does not exist on expected with gray color", () => {
    render(
      <DataQualityTag
        // @ts-ignore
        dataQuality={"RANDOM"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const notSelected = screen.getByText(/Not selected/i);
    expect(notSelected).toBeInTheDocument();

    const notSelectedColor = screen.getByTestId("random-container");
    expect(notSelectedColor).toHaveStyle(
      "background-color: var(--chakra-colors-gray-100)"
    );
  });

  it("should show Caution if dataQuality is CAUTION with red color", () => {
    render(
      <DataQualityTag
        dataQuality={"CAUTION"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const caution = screen.getByText(/Caution/);
    expect(caution).toBeInTheDocument();

    const cautionColor = screen.getByTestId("caution-container");
    expect(cautionColor).toHaveStyle(
      "background-color: var(--chakra-colors-red-100)"
    );
  });

  it("should show Acceptable if dataQuality is ACCEPTABLE with blue color", () => {
    render(
      <DataQualityTag
        dataQuality={"ACCEPTABLE"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const acceptable = screen.getByText(/Acceptable/);
    expect(acceptable).toBeInTheDocument();

    const acceptableColor = screen.getByTestId("acceptable-container");
    expect(acceptableColor).toHaveStyle(
      "background-color: var(--chakra-colors-blue-100)"
    );
  });

  it("should show Good if dataQuality is GOOD with green color", () => {
    render(
      <DataQualityTag
        dataQuality={"GOOD"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const good = screen.getByText(/Good/);
    expect(good).toBeInTheDocument();

    const goodColor = screen.getByTestId("good-container");
    expect(goodColor).toHaveStyle(
      "background-color: var(--chakra-colors-green-100)"
    );
  });

  it("should show Excellent if dataQuality is EXCELLENT with orange color", () => {
    render(
      <DataQualityTag
        dataQuality={"EXCELLENT"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const excellent = screen.getByText(/Excellent/);
    expect(excellent).toBeInTheDocument();

    const excellentColor = screen.getByTestId("excellent-container");
    expect(excellentColor).toHaveStyle(
      "background-color: var(--chakra-colors-orange-100)"
    );
  });

  it("should call setDataQuality when clicked", () => {
    render(
      <DataQualityTag
        dataQuality={"EXCELLENT"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const excellent = screen.getByText(/Excellent/);
    expect(excellent).toBeInTheDocument();

    const excellentButton = screen.getByText(/EXCELLENT/);

    excellentButton.click();
    expect(mockSetDataQuality).toHaveBeenCalledWith("EXCELLENT");
  });

  it("should change the shown dataQuality when clicked", () => {
    render(
      <DataQualityTag
        dataQuality={"EXCELLENT"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const excellent = screen.getByText(/Excellent/);
    const good = screen.getByText(/Good/);
    expect(excellent).toBeInTheDocument();
    expect(good).not.toBeInTheDocument();

    const goodButton = screen.getByText(/GOOD/);
    goodButton.click();

    expect(mockSetDataQuality).toHaveBeenCalledWith("GOOD");
    expect(excellent).not.toBeInTheDocument();
    expect(good).toBeInTheDocument();
  });
});
