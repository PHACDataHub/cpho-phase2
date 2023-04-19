import { FileColumnData } from "./constants";

export type Category = {
  id: number;
  label: string;
};

export type SubCategory = {
  id: number;
  label: string;
  category: number;
};

export type LocationType =
  | "AB"
  | "BC"
  | "MB"
  | "NB"
  | "NL"
  | "NS"
  | "NT"
  | "NU"
  | "ON"
  | "PE"
  | "QC"
  | "SK"
  | "YT"
  | "CANADA"
  | "ATLANTIC"
  | "PRAIRIE"
  | "TERRITORIES";

export type GeographyType = "COUNTRY" | "PROVINCE_TERRITORY" | "REGION";

export type DataQualityType = "CAUTION" | "ACCEPTABLE" | "GOOD" | "EXCELLENT";

export type DataPoint = {
  id: string;
  indicatorId?: number;
  locationType: GeographyType;
  location: LocationType;
  sex: string;
  gender: string;
  ageGroup: string;
  ageGroupType: string;
  dataQuality: DataQualityType;
  value: number;
  valueLowerBound: number;
  valueUpperBound: number;
  valueUnit: string;
  singleYearTimeframe?: number;
  multiYearTimeframe?: [number, number];
};

export type DataPointField = {
  name: string;
  id: string;
  required?: boolean;
  dpField: keyof DataPoint;
  type: "text" | "number" | "select";
  options?: {
    value: string;
    label: string;
  }[];
  placeholder?: string;
};

export type FileFormat = keyof typeof FileColumnData;

export type PossibleIndicatorType = {
  id: number;
  name: string;
  dataPointCount: number;
  category: string;
};

export type IndicatorType = {
  id: number;
  category: string;
  subCategory: string;
  name: string;
  detailedIndicator: string;
  subIndicatorMeasurement: string;
  indicatordataSet: DataPoint[];
};

export type ErrorType = {
  dataPointId: string;
  field: string;
  message: string;
};
