import {
  VStack,
  FormControl,
  FormLabel,
  Input,
  Select,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { categories, sub_categories } from "../../utils/constants";
import { SubCategory } from "../../utils/types";

type Props = {
  indicatorName: string;
  detailedIndicator: string;
  category: number;
  subCategory: number;
  setField: (field: string, value: any) => void;
};

const IndicatorGenInfo = ({
  indicatorName,
  detailedIndicator,
  category,
  subCategory,
  setField,
}: Props) => {
  const [filteredSubCategories, setFilteredSubCategories] =
    useState<SubCategory[]>(sub_categories);

  useEffect(() => {
    setFilteredSubCategories(
      sub_categories.filter((c) => c.category === category)
    );
  }, [category]);

  return (
    <VStack spacing={5} w="100%">
      <FormControl isRequired>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Indicator Name
        </FormLabel>
        <Input
          value={indicatorName}
          onChange={(e) => setField("indicatorName", e.target.value)}
          required
          variant="filled"
          placeholder="Enter indicator name"
        />
      </FormControl>
      <FormControl isRequired>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Category
        </FormLabel>
        <Select
          required
          variant="filled"
          value={category}
          onChange={(e) => setField("category", parseInt(e.target.value))}
        >
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.label}
            </option>
          ))}
        </Select>
      </FormControl>
      <FormControl>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Sub Category
        </FormLabel>
        <Select
          variant="filled"
          value={subCategory}
          onChange={(e) => setField("subCategory", parseInt(e.target.value))}
        >
          {filteredSubCategories.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </Select>
      </FormControl>
      <FormControl>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Detailed Indicator
        </FormLabel>
        <Input
          value={detailedIndicator}
          onChange={(e) => setField("detailedIndicator", e.target.value)}
          variant="filled"
          placeholder="Enter detailed indicator"
        />
      </FormControl>
    </VStack>
  );
};

export default IndicatorGenInfo;
