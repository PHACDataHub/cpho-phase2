import { Category, DataPointField, SubCategory } from "./types";

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

export const IndicatorDataFields: DataPointField[] = [
  {
    name: "Geography",
    id: "dp_geography",
    type: "select",
    dpField: "geography",
    required: true,
    options: [
      {
        value: "COUNTRY",
        label: "Country",
      },
      {
        value: "PROVINCE_TERRITORY",
        label: "Province or Territory",
      },
      {
        value: "REGION",
        label: "Region",
      },
    ],
    placeholder: "e.g. Country, Province",
  },
  {
    name: "Location",
    id: "dp_location",
    type: "select",
    dpField: "country",
    required: true,
    options: [
      {
        value: "AB",
        label: "Alberta",
      },
      {
        value: "BC",
        label: "British Columbia",
      },
      {
        value: "MN",
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
      {
        value: "CANADA",
        label: "Canada",
      },
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
    ],
    placeholder: "e.g. Canada; Ontario",
  },
  {
    name: "Sex",
    id: "dp_sex",
    dpField: "sex",
    type: "text",
    placeholder: "e.g. Males",
  },
  {
    name: "Gender",
    id: "dp_gender",
    dpField: "gender",
    type: "text",
  },
  {
    name: "Age Group",
    id: "dp_age_group",
    type: "text",
    dpField: "ageGroup",
    placeholder: "e.g. 14-24; 8th grade",
  },
  {
    name: "Age Group Type",
    id: "dp_age_group_type",
    dpField: "ageGroupType",
    type: "text",
    placeholder: "e.g. decade; grade",
  },
  {
    name: "Data Quality",
    id: "dp_data_quality",
    dpField: "dataQuality",
    type: "select",
    required: true,
    options: [
      {
        value: "CAUTION",
        label: "Caution",
      },
      {
        value: "ACCEPTABLE",
        label: "Acceptable",
      },
      {
        value: "GOOD",
        label: "Good",
      },
      {
        value: "VERY_GOOD",
        label: "Very Good",
      },
    ],
  },
  {
    name: "Value",
    id: "dp_value",
    dpField: "value",
    type: "number",
    required: true,
  },
  {
    name: "Value Lower Bound",
    id: "dp_value_lower_bound",
    dpField: "valueLowerBound",
    type: "number",
  },
  {
    name: "Value Upper Bound",
    id: "dp_value_upper_bound",
    dpField: "valueUpperBound",
    type: "number",
  },
  {
    name: "Value Unit",
    id: "dp_value_unit",
    dpField: "valueUnit",
    type: "text",
    required: true,
    placeholder: "e.g. percentage; years; rate per 100,000",
  },
];

export const FileColumnData = {
  indicator: [
    "Category",
    "Topic",
    "Indicator",
    "Detailed_Indicator",
    "Sub_Indicator_Measurement",
    "Country",
    "Geography",
    "Sex",
    "Gender",
    "Age_Group",
    "Age_Group_Type",
    "Data_Quality",
    "Value",
    "Value_LowerCI",
    "Value_UpperCI",
    "Value_Units",
    "SingleYear_TimeFrame",
    "MultiYear_TimeFrame",
  ],
  trendAnalysis: [
    "Indicator",
    "Detailed_Indicator",
    "Year",
    "DataPoint",
    "LineOfBestFitPoint",
  ],
  benchmarking: [
    "Indicator",
    "Detailed_Indicator",
    "Unit",
    "OCED_Country",
    "Value",
    "Year",
    "Standard_Deviation",
    "Comparison_to_OECD_average",
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
