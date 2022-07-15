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
    name: "Country",
    id: "dp_country",
    type: "text",
  },
  {
    name: "Geography",
    id: "dp_geography",
    type: "text",
  },
  {
    name: "Sex",
    id: "dp_sex",
    type: "text",
  },
  {
    name: "Gender",
    id: "dp_gender",
    type: "text",
  },
  {
    name: "Age Group",
    id: "dp_age_group",
    type: "text",
  },
  {
    name: "Age Group Type",
    id: "dp_age_group_type",
    type: "text",
  },
  {
    name: "Data Quality",
    id: "dp_data_quality",
    type: "text",
  },
  {
    name: "Value",
    id: "dp_value",
    type: "number",
  },
  {
    name: "Value Lower Bound",
    id: "dp_value_lower_bound",
    type: "number,",
  },
  {
    name: "Value Upper Bound",
    id: "dp_value_upper_bound",
    type: "number",
  },
  {
    name: "Value Unit",
    id: "dp_value_unit",
    type: "text",
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
