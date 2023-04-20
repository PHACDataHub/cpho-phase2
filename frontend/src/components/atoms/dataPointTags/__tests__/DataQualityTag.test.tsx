import { screen } from "@testing-library/react";
import { render } from "../../../../test-utils";
import DataQualityTag from "../DataQualityTag";

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

    const caution = screen.getAllByText(/Caution/);
    expect(caution).toBeTruthy();

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

    const acceptable = screen.getAllByText(/Acceptable/);
    expect(acceptable).toBeTruthy();

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

    const good = screen.getAllByText(/Good/);
    expect(good).toBeTruthy();

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

    const excellent = screen.getAllByText(/Excellent/);
    expect(excellent).toBeTruthy();

    const excellentColor = screen.getByTestId("excellent-container");
    expect(excellentColor).toHaveStyle(
      "background-color: var(--chakra-colors-orange-100)"
    );
  });

  it("should call setDataQuality when clicked", () => {
    render(
      <DataQualityTag
        dataQuality={"CAUTION"}
        setDataQuality={mockSetDataQuality}
      />
    );

    const caution = screen.findAllByText(/Caution/);
    expect(caution).toBeTruthy();

    const excellentButton = screen.getAllByText(/Excellent/)[0];

    excellentButton?.click();
    expect(mockSetDataQuality).toHaveBeenCalledWith("EXCELLENT");
  });
});
