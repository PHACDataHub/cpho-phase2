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
      name
    }
  }
`;

export const GET_INDICATOR_DATA = gql`
  query ($id: Int!) {
    indicator(id: $id) {
      id
      category
      subCategory
      name
      detailedIndicator
      subIndicatorMeasurement
      indicatordataSet {
        id
        locationType
        location
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

export const GET_INDICATOR_DATA_BY_IDS = gql`
  query ($ids: [Int]) {
    indicatorsById(ids: $ids) {
      id
      category
      subCategory
      name
      detailedIndicator
      subIndicatorMeasurement
      indicatordataSet {
        locationType
        location
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
