import { gql } from "@apollo/client";

export const GET_INDICATOR_OVERVIEW = gql`
  query {
    possibleIndicators {
      id
      name
      category
      dataPointCount
    }
  }
`;

export const GET_INDICATORS_AND_IDS = gql`
  query {
    indicators {
      id
      indicator
    }
  }
`;

export const GET_INDICATOR_DATA = gql`
  query ($id: Int!) {
    indicator(id: $id) {
      id
      category
      topic
      indicator
      detailedIndicator
      subIndicatorMeasurement
      indicatordataSet {
        id
        country
        geography
        sex
        gender
        ageGroup
        ageGroupType
        dataQuality
        value
        valueLowerBound
        valueUpperBound
        valueUnit
        singleYearTimeframe
        multiYearTimeframe
      }
    }
  }
`;
