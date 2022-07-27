import {
  VStack,
  Heading,
  Input,
  Select,
  Button,
  Stack,
  FormControl,
  FormLabel,
} from "@chakra-ui/react";
import { FormEvent, useEffect, useState } from "react";
import { categories, sub_categories } from "../utils/constants";
import { useSmallScreen } from "../utils/hooks";
import { DataPoint, SubCategory } from "../utils/types";
import { AddDataPointButton } from "./components/AddDataPointButton";
import { DataPointContainer } from "./components/DataPointContainer";
import { Page } from "./Page";

export function AddIndicator() {
  const [indicatorName, setIndicatorName] = useState("");
  const [detailedIndicator, setDetailedIndicator] = useState("");
  const [category, setCategory] = useState(1);
  const [subCategory, setSubCategory] = useState(1);
  const [filteredSubCategories, setFilteredSubCategories] =
    useState<SubCategory[]>(sub_categories);
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([]);
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [statusMessage, setStatusMessage] = useState("");

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
    <VStack spacing={5} w={smallScreen ? "90%" : "50%"}>
      <FormControl isRequired>
        <FormLabel fontSize="2xl" fontWeight="bold">
          Indicator Name
        </FormLabel>
        <Input
          value={indicatorName}
          onChange={(e) => setIndicatorName(e.target.value)}
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
          onChange={(e) => setCategory(parseInt(e.target.value))}
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
          onChange={(e) => setSubCategory(parseInt(e.target.value))}
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
          onChange={(e) => setDetailedIndicator(e.target.value)}
          variant="filled"
          placeholder="Enter detailed indicator"
        />
      </FormControl>
    </VStack>
  );

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    setStatus("loading");
    // console.log("Submitting form", event);
    // let formData = new FormData(event.target as HTMLFormElement);
    let formData = new FormData();

    formData.append("indicator_name", indicatorName);
    formData.append(
      "category",
      categories.find((c) => c.id === category)?.label ?? ""
    );
    formData.append(
      "sub_category",
      sub_categories.find((c) => (c.id = subCategory))?.label ?? ""
    );
    formData.append("detailed_indicator", detailedIndicator);
    formData.append("data_points", JSON.stringify(dataPoints));

    formData.forEach((value, key) => console.log(key, value));
    fetch(
      (process.env.REACT_APP_SERVER_URL || "http://localhost:8000/") +
        "api/addindicator",
      {
        method: "POST",
        body: formData,
      }
    ).then(async (response) => {
      const obj = await response.json();
      console.log("RESPONSE", obj);
      setStatus(obj.status);
      setStatusMessage(obj.message);
    });
  };

  return (
    <Page backButton={{ show: true, redirectUrl: "/" }} title="Add Indicator">
      <Stack
        direction={smallScreen ? "column" : "row"}
        w={smallScreen ? "95%" : "90%"}
        margin="auto"
        my={10}
        display="flex"
        justify="space-around"
        align="flex-start"
      >
        {generalInfo}
        <VStack w={smallScreen ? "90%" : "50%"}>
          <AddDataPointButton
            dataPoints={dataPoints}
            setDataPoints={setDataPoints}
          />
          <DataPointContainer
            setDataPoints={setDataPoints}
            dataPoints={dataPoints}
          />
        </VStack>
      </Stack>
      <VStack>
        {statusMessage && (
          <Heading
            size="md"
            color={status === "success" ? "green.500" : "red.500"}
          >
            {statusMessage}
          </Heading>
        )}
        <Button
          w="40%"
          disabled={dataPoints.length === 0}
          colorScheme="green"
          onClick={onSubmit}
        >
          Submit
        </Button>
      </VStack>
    </Page>
  );
}
