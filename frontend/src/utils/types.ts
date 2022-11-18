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

export type DataPoint = {
  indicatorId?: number;
  country: string;
  geography: string;
  sex: string;
  gender: string;
  ageGroup: string;
  ageGroupType: string;
  dataQuality: string;
  value: number;
  valueLowerBound: number;
  valueUpperBound: number;
  valueUnit: string;
  singleYearTimeframe?: string;
  multiYearTimeframe?: string;
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
