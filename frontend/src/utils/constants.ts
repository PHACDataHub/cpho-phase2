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
