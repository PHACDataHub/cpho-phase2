import {
  VStack,
  FormControl,
  FormLabel,
  Input,
  Select,
} from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import { categories, sub_categories } from "../../utils/constants";
import IndicatorFormContext from "../../utils/context/IndicatorFormContext";
import { SubCategory } from "../../utils/types";

type Props = {
  categoryId: number;
  subCategoryId: number;
};

const IndicatorGenInfo = ({ categoryId, subCategoryId }: Props) => {
  const [filteredSubCategories, setFilteredSubCategories] =
    useState<SubCategory[]>(sub_categories);

  useEffect(() => {
    setFilteredSubCategories(
      sub_categories.filter((c) => c.category === categoryId)
    );
  }, [categoryId]);

  const { indicator, setField } = useContext(IndicatorFormContext);

  return (
    <VStack spacing={5} w={["98%", "75%", "65%", "40%"]}>
      <FormControl isRequired>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Indicator Name
        </FormLabel>
        <Input
          value={indicator?.indicator}
          onChange={(e) => setField("indicator", e.target.value)}
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
          value={categoryId}
          onChange={(e) => {
            setField(
              "category",
              categories.find((c) => c.id === parseInt(e.target.value))?.label
            );
          }}
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
          value={subCategoryId}
          onChange={(e) => {
            setField(
              "topic",
              sub_categories.find((c) => c.id === parseInt(e.target.value))
                ?.label
            );
          }}
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
          value={indicator?.detailedIndicator}
          onChange={(e) => setField("detailedIndicator", e.target.value)}
          variant="filled"
          placeholder="Enter detailed indicator"
        />
      </FormControl>
    </VStack>
  );
};

export default IndicatorGenInfo;
