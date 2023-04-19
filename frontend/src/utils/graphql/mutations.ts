import { gql } from "@apollo/client";

export const CREATE_INDICATOR = gql`
  mutation CreateIndicator(
    $category: String!
    $detailedIndicator: String!
    $name: String!
    $subIndicatorMeasurement: String
    $subCategory: String!
    $dataPoints: [DataPointArgsInput]!
  ) {
    createIndicator(
      category: $category
      detailedIndicator: $detailedIndicator
      name: $name
      subIndicatorMeasurement: $subIndicatorMeasurement
      subCategory: $subCategory
      dataPoints: $dataPoints
    ) {
      indicator {
        name
        category
      }
      dataPoints {
        id
      }
    }
  }
`;

export const MODIFY_INDICATOR = gql`
  mutation ModifyIndicator(
    $category: String!
    $dataPoints: [DataPointArgsInput]!
    $detailedIndicator: String!
    $id: Int!
    $name: String!
    $subIndicatorMeasurement: String
    $subCategory: String!
  ) {
    modifyIndicator(
      category: $category
      dataPoints: $dataPoints
      detailedIndicator: $detailedIndicator
      id: $id
      name: $name
      subIndicatorMeasurement: $subIndicatorMeasurement
      subCategory: $subCategory
    ) {
      success
      indicator {
        name
        category
        subCategory
      }
      dataPoints {
        locationType
        location
      }
    }
  }
`;
