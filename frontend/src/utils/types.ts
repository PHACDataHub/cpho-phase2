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
  indicator_id: number;
  country: string;
  geography: string;
  sex: string;
  gender: string;
  age_group: string;
  age_group_type: string;
  data_quality: string;
  value: number;
  value_lower_bound: number;
  value_upper_bound: number;
  value_unit: string;
  single_year_timeframe: string;
  multi_year_timeframe: string;
};
