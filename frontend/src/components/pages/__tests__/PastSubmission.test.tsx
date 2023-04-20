import { render } from "../../../test-utils";
import {
  GET_INDICATORS_AND_IDS,
  GET_INDICATOR_DATA,
} from "../../../utils/graphql/queries";
import { ModifyPastSubmissions } from "../PastSubmission";
import { MockedProvider } from "@apollo/client/testing";
import { BrowserRouter } from "react-router-dom";
import { IndicatorType } from "../../../utils/types";

const mocks = [
  {
    request: {
      query: GET_INDICATORS_AND_IDS,
    },
    result: {
      data: {
        indicators: [
          {
            id: 1,
            name: "Test Indicator",
          },
        ] as IndicatorType[],
      },
    },
  },
  {
    request: {
      query: GET_INDICATOR_DATA,
      variables: { id: 1 },
    },
    result: {
      data: {
        indicator: {
          id: 1,
          name: "Test Indicator",
          indicatordataSet: [],
          category: "Test Category",
          subCategory: "Test Topic",
          detailedIndicator: "Test Detailed Indicator",
          subIndicatorMeasurement: "Test Sub Indicator Measurement",
        } as IndicatorType,
      },
    },
  },
];

describe("PastSubmission", () => {
  it("should render", async () => {
    const { container, findByText } = render(
      <BrowserRouter>
        <MockedProvider mocks={mocks} addTypename={false}>
          <ModifyPastSubmissions />
        </MockedProvider>
      </BrowserRouter>
    );

    expect(container).toBeTruthy();

    expect(await findByText("Test Indicator")).toBeInTheDocument();
  });
});
