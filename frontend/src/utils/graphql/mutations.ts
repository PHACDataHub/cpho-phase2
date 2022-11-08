import { gql } from "@apollo/client";

export const CREATE_INDICATOR = gql`
  mutation CreateIndicator(
    $category: String!
    $detailedIndicator: String!
    $indicator: String!
    $subIndicatorMeasurement: String
    $topic: String!
    $dataPoints: [DataPointArgsInput]!
  ) {
    createIndicator(
      category: $category
      detailedIndicator: $detailedIndicator
      indicator: $indicator
      subIndicatorMeasurement: $subIndicatorMeasurement
      topic: $topic
      dataPoints: $dataPoints
    ) {
      indicator {
        indicator
        category
      }
      dataPoints {
        id
      }
    }
  }
`;
