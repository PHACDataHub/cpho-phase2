import {
  VStack,
  Text,
  Box,
  Heading,
  Input,
  Select,
  SelectField,
  HStack,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  FormHelperText,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { categories, sub_categories } from "../utils/constants";
import { useSmallScreen } from "../utils/hooks";
import { Category, SubCategory } from "../utils/types";
import { AddDataPointButton } from "./components/AddDataPointButton";
import { Page } from "./Page";

export function AddIndicator() {
  const [category, setCategory] = useState<number>(1);
  const [subCategory, setSubCategory] = useState<number>(1);
  const [filteredSubCategories, setFilteredSubCategories] =
    useState<SubCategory[]>(sub_categories);
  const [dataPoints, setDataPoints] = useState([]);

  const smallScreen = useSmallScreen();

  useEffect(() => {
    // console.log("Selected category: ", category);
    // console.log("Looking through", sub_categories);
    // console.log(
    //   "Filtered: ",
    //   sub_categories.filter((c) => {
    //     console.log("Comparing ", c.category, " to ", category);
    //     return c.category === category;
    //   })
    // );
    setFilteredSubCategories(
      sub_categories.filter((c) => c.category === category)
    );
  }, [category]);

  const generalInfo = (
    <VStack spacing={5} w="40%">
      <Heading>Indicator Name</Heading>
      <Input required variant="filled" placeholder="Enter indicator name" />
      <Heading>Category</Heading>
      <Select
        required
        variant="filled"
        onChange={(e) => setCategory(parseInt(e.target.value))}
      >
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.label}
          </option>
        ))}
      </Select>
      <Heading>Sub Category</Heading>
      <Select
        required
        variant="filled"
        onChange={(e) => setSubCategory(parseInt(e.target.value))}
      >
        {filteredSubCategories.map((s) => (
          <option key={s.id} value={s.id}>
            {s.label}
          </option>
        ))}
      </Select>
    </VStack>
  );

  return (
    <Page backButton={{ show: true, redirectUrl: "/" }} title="Add Indicator">
      <VStack w={smallScreen ? "95%" : "90%"} margin="auto" my={10}>
        <HStack w="100%" justify="space-around" align="flex-start">
          {generalInfo}
          <AddDataPointButton />
        </HStack>
      </VStack>
    </Page>
  );
}
