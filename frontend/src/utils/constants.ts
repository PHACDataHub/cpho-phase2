import { Category, SubCategory } from "./types";

export const categories: Category[] = [
  {
    id: 1,
    label: "Factors Influencing Health",
  },
  {
    id: 2,
    label: "General Health Status",
  },
  {
    id: 3,
    label: "Health Outcomes",
  },
];

export const sub_categories: SubCategory[] = [
  {
    id: 1,
    label: "Childhood and Family Risk and Protective Factors",
    category: 1,
  },
  {
    id: 2,
    label: "Social Factors",
    category: 1,
  },
  {
    id: 3,
    label: "Substance Use",
    category: 1,
  },
  {
    id: 4,
    label: "Health Status",
    category: 2,
  },
  {
    id: 5,
    label: "Chronic Diseases and Mental Health",
    category: 3,
  },
  {
    id: 6,
    label: "Communicable Diseases",
    category: 3,
  },
];

export const ProvincesTerritories = [
  {
    value: "AB",
    label: "Alberta",
  },
  {
    value: "BC",
    label: "British Columbia",
  },
  {
    value: "MB",
    label: "Manitoba",
  },
  {
    value: "NB",
    label: "New Brunswick",
  },
  {
    value: "NL",
    label: "Newfoundland and Labrador",
  },
  {
    value: "NT",
    label: "Northwest Territories",
  },
  {
    value: "NS",
    label: "Nova Scotia",
  },
  {
    value: "NU",
    label: "Nunavut",
  },
  {
    value: "ON",
    label: "Ontario",
  },
  {
    value: "PE",
    label: "Prince Edward Island",
  },
  {
    value: "QC",
    label: "Quebec",
  },
  {
    value: "SK",
    label: "Saskatchewan",
  },
  {
    value: "YT",
    label: "Yukon",
  },
];

export const Regions = [
  {
    value: "ATLANTIC",
    label: "Atlantic",
  },
  {
    value: "PRAIRIE",
    label: "Prairie",
  },
  {
    value: "TERRITORIES",
    label: "Territories",
  },
];

export const FileColumnData = {
  indicator: [
    {
      label: "Category",
      value: "category",
      required: true,
      matches: ["category", "categories", "Category", "Categories"],
      example: "General Health Status",
    },
    {
      label: "Sub Category",
      value: "subCategory",
      required: true,
      matches: [
        "subcategory",
        "subcategories",
        "sub category",
        "sub categories",
        "sub_category",
        "topic",
      ],
      example: "Childhood and Family Factors",
    },
    {
      label: "Indicator Name",
      value: "indicatorName",
      required: true,
      matches: ["indicatorname", "indicator", "indicator name"],
      example: "Lung Cancer",
    },
    {
      label: "Detailed Indicator",
      value: "detailedIndicator",
      matches: [
        "detailedindicator",
        "detailedindicators",
        "detailed indicator",
        "detailed indicators",
        "detailed_indicator",
      ],
      example:
        "Rate of newly diagnoses cases of lung cancer per 100,000 people",
    },
    {
      label: "Sub Indicator Measurement",
      value: "subIndicatorMeasurement",
      matches: [
        "subindicatormeasurement",
        "sub_indicator_measurement",
        "sub indicator measurement",
      ],
    },
    {
      label: "Location",
      value: "location",
      required: true,
      matches: ["location"],
      example: "Canada, Ontario, etc.",
    },
    {
      label: "Location Type",
      value: "locationType",
      required: true,
      matches: ["locationtype", "location type", "location_type"],
      example: "Country, Province/Territory, Region",
    },
    { label: "Sex", value: "sex", matches: ["sex"] },
    { label: "Gender", value: "gender", matches: ["gender"] },
    {
      label: "Age Group",
      value: "ageGroup",
      matches: ["agegroup", "age group", "age_group"],
    },
    {
      label: "Age Group Type",
      value: "ageGroupType",
      matches: ["agegrouptype", "age group type", "age_group_type"],
    },
    {
      label: "Data Quality",
      value: "dataQuality",
      required: true,
      matches: ["dataquality", "data quality", "data_quality"],
    },
    {
      label: "Value",
      value: "value",
      required: true,
      matches: ["value"],
    },
    {
      label: "Value Lower Bound",
      value: "valueLowerBound",
      matches: ["valuelowerbound", "value lower bound", "value_lower_bound"],
    },
    {
      label: "Value Upper Bound",
      value: "valueUpperBound",
      matches: ["valueupperBound", "value upper bound", "value_upper_bound"],
    },
    {
      label: "Value Unit",
      value: "valueUnit",
      required: true,
      matches: ["valueunit", "value unit", "value_unit"],
    },
    {
      label: "Single Year TimeFrame",
      value: "singleYearTimeFrame",
      required: true,
      matches: [
        "singleyeartimeframe",
        "single year timeframe",
        "year",
        "single_year_timeframe",
      ],
    },
    {
      label: "Multi Year TimeFrame",
      value: "multiYearTimeFrame",
      matches: [
        "multiyeartimeframe",
        "multi year timeframe",
        "multi_year_timeframe",
      ],
    },
  ],
  trendAnalysis: [
    { label: "Indicator", value: "indicator", required: true },
    { label: "Detailed Indicator", value: "detailedIndicator", required: true },
    { label: "Year", value: "year", required: true },
    { label: "Data Point", value: "dataPoint", required: true },
    { label: "Line of Best Fit Point", value: "lineOfBestFitPoint" },
  ],
  benchmarking: [
    { label: "Indicator", value: "indicator", required: true },
    { label: "Detailed Indicator", value: "detailedIndicator", required: true },
    { label: "Unit", value: "unit", required: true },
    { label: "OCED Country", value: "oecdCountry", required: true },
    { label: "Value", value: "value", required: true },
    { label: "Year", value: "year", required: true },
    { label: "Standard Deviation", value: "standardDeviation" },
    { label: "Comparison to OECD average", value: "comparisonToOecdAverage" },
  ],
};

export const PossibleIndicators = [
  {
    id: 1,
    label: "Adult Obesity",
    category: 3,
    subCategory: 5,
  },
  {
    id: 2,
    label: "Cannabis Use",
    category: 1,
    subCategory: 3,
  },
];
