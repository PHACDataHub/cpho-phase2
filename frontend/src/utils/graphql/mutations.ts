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

export const MODIFY_INDICATOR = gql`
  mutation ModifyIndicator(
    $category: String!
    $dataPoints: [DataPointArgsInput]!
    $detailedIndicator: String!
    $id: Int!
    $indicator: String!
    $subIndicatorMeasurement: String
    $topic: String!
  ) {
    modifyIndicator(
      category: $category
      dataPoints: $dataPoints
      detailedIndicator: $detailedIndicator
      id: $id
      indicator: $indicator
      subIndicatorMeasurement: $subIndicatorMeasurement
      topic: $topic
    ) {
      success
      indicator {
        indicator
        topic
        category
      }
      dataPoints {
        country
        geography
      }
    }
  }
`;

export const IMPORT_DATA = gql`
  mutation ImportData($file: Upload!) {
    importData(file: $file) {
      success
    }
  }
`;

export const EXPORT_DATA = gql`
  mutation ExportData($selectedIndicators: [Int]!) {
    exportData(selectedIndicators: $selectedIndicators) {
      csvFile {
        id
        fileUrl
      }
    }
  }
`;
