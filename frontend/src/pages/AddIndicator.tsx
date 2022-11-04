import { gql, useMutation } from "@apollo/client";
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
  const [filteredSubCategories, setFilteredSubCategories] =
    useState<SubCategory[]>(sub_categories);

  const [values, setValues] = useState({
    indicatorName: "",
    detailedIndicator: "",
    category: 1,
    subCategory: 1,
    dataPoints: [] as DataPoint[],
  });

  const {
    indicatorName,
    detailedIndicator,
    category,
    subCategory,
    dataPoints,
  } = values;

  const setField = (field: string, value: any) => {
    setValues({
      ...values,
      [field]: value,
    });
  };

  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [statusMessage, setStatusMessage] = useState("");

  const smallScreen = useSmallScreen();

  useEffect(() => {
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

  const CREATE_INDICATOR = gql`
    mutation CreateIndicator(
      $category: String!
      $detailedIndicator: String!
      $indicator: String!
      $subIndicatorMeasurement: String
      $topic: String!
      $dataPoints: [DataPointArgsInput]!
    ) {
      createIndicator(
        category: $category
        detailedIndicator: $detailedIndicator
        indicator: $indicator
        subIndicatorMeasurement: $subIndicatorMeasurement
        topic: $topic
        dataPoints: $dataPoints
      ) {
        indicator {
          indicator
          category
        }
        dataPoints {
          id
        }
      }
    }
  `;
  const [createIndicator, { loading, error, data }] =
    useMutation(CREATE_INDICATOR);

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
            setDataPoints={(d) => setField("dataPoints", d)}
          />
          <DataPointContainer
            setDataPoints={(d) => setField("dataPoints", d)}
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
          onClick={() => {
            createIndicator({
              variables: {
                category:
                  categories.find((c) => c.id === category)?.label ?? "",
                detailedIndicator,
                indicator: indicatorName,
                subIndicatorMeasurement: "",
                topic:
                  sub_categories.find((c) => c.id === subCategory)?.label ?? "",
                dataPoints,
              },
            });
          }}
        >
          Submit
        </Button>
      </VStack>
    </Page>
  );
}
