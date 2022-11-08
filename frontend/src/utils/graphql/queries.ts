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
