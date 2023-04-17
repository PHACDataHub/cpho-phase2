import {
  Button,
  ButtonGroup,
  Heading,
  Stack,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { Page } from "../template/Page";
import { RiFileExcel2Fill } from "react-icons/ri";
import { FaFileCsv } from "react-icons/fa";
import { useMutation, useQuery } from "@apollo/client";
import {
  GET_INDICATOR_DATA_BY_IDS,
  GET_INDICATOR_OVERVIEW,
} from "../../utils/graphql/queries";
import { PossibleIndicatorType } from "../../utils/types";
import PossibleIndicatorBox from "../molecules/PossibleIndicatorBox";
import ExportIndicatorList from "../organisms/ExportIndicatorList";
import { IndicatorType } from "../../utils/types";

export function ExportPage() {
  const toast = useToast();
  const [fileType, setFileType] = useState<"excel" | "csv" | "sql">("csv");
  const [fileLoad, setFileLoad] = useState(false);

  const [selectedIndicators, setSelectedIndicators] = useState<
    PossibleIndicatorType[]
  >([]);

  const [finalSelectedIds, setFinalSelectedIds] = useState<number[]>([]);

  const addSelected = useCallback(
    (ind: PossibleIndicatorType) => {
      if (!selectedIndicators.includes(ind)) {
        setSelectedIndicators([...selectedIndicators, ind]);
      }
    },
    [selectedIndicators]
  );

  const removeSelected = useCallback(
    (ind: PossibleIndicatorType) => {
      if (selectedIndicators.includes(ind)) {
        const idx = selectedIndicators.indexOf(ind);
        setSelectedIndicators(
          selectedIndicators
            .slice(0, idx)
            .concat(selectedIndicators.slice(idx + 1))
        );
      }
    },
    [selectedIndicators]
  );

  const toggleSelected = useCallback(
    (ind: PossibleIndicatorType) => {
      if (selectedIndicators.includes(ind)) {
        removeSelected(ind);
      } else {
        addSelected(ind);
      }
    },
    [selectedIndicators, addSelected, removeSelected]
  );

  const {
    loading: exportLoading,
    data: exportData,
    error: exportError,
  } = useQuery(GET_INDICATOR_DATA_BY_IDS, {
    variables: {
      ids: finalSelectedIds,
    },
  });

  useEffect(() => {
    if (
      fileLoad &&
      exportData &&
      exportData.indicatorsById &&
      exportData.indicatorsById.length > 0
    ) {
      const indicatorsData = exportData.indicatorsById
        .map((ind: IndicatorType) => {
          return ind.indicatordataSet
            .map((dp) => {
              return [
                ind.category ? `"${ind.category}"` : null,
                ind.topic ? `"${ind.topic}"` : null,
                ind.indicator ? `"${ind.indicator}"` : null,
                ind.detailedIndicator ? `"${ind.detailedIndicator}"` : null,
                ind.subIndicatorMeasurement
                  ? `"${ind.subIndicatorMeasurement}"`
                  : null,
                dp.country ? `"${dp.country}"` : null,
                dp.geography ? `"${dp.geography}"` : null,
                dp.sex ? `"${dp.sex}"` : null,
                dp.gender ? `"${dp.gender}"` : null,
                dp.ageGroup ? `"${dp.ageGroup}"` : null,
                dp.ageGroupType ? `"${dp.ageGroupType}"` : null,
                dp.dataQuality ? `"${dp.dataQuality}"` : null,
                dp.value ? `"${dp.value}"` : null,
                dp.valueLowerBound ? `"${dp.valueLowerBound}"` : null,
                dp.valueUpperBound ? `"${dp.valueUpperBound}"` : null,
                dp.valueUnit ? `"${dp.valueUnit}"` : null,
                dp.singleYearTimeframe ? `"${dp.singleYearTimeframe}"` : null,
                dp.multiYearTimeframe ? `"${dp.multiYearTimeframe}"` : null,
              ].join(",");
            })
            .join("\n");
        })
        .join("\n");

      const csvData =
        "category,topic,indicator,detailed_indicator,sub_indicator_measurement,country,geography,sex,gender,age_group,age_group_type,data_quality,value,value_lower_bound,value_upper_bound,value_unit,single_year_timeframe,multi_year_timeframe\n" +
        indicatorsData;

      console.log(csvData);

      const blob = new Blob([csvData], { type: "text/csv" });
      const link = document.createElement("a");
      link.setAttribute("href", URL.createObjectURL(blob));
      link.setAttribute("download", "export.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast({
        title: "Data exported",
        description:
          "The data you requested has been downloaded to your computer",
        status: "success",
        duration: 4000,
        isClosable: true,
      });
      setFileLoad(false);
    }
  }, [exportData, toast]);

  const handleExport = async () => {
    setFileLoad(true);
    setFinalSelectedIds(selectedIndicators.map((ind) => ind.id));
  };

  const { loading, error, data } = useQuery<{
    possibleIndicators: {
      id: number;
      name: string;
      category: string;
      dataPointCount: number;
    }[];
  }>(GET_INDICATOR_OVERVIEW, {
    fetchPolicy: "network-only",
  });

  const possibleIndicators = data?.possibleIndicators;

  return (
    <Page title="Export data" backButton={{ show: true, redirectUrl: "/" }}>
      <VStack spacing={8}>
        {loading && (
          <Heading size="lg" mx="auto">
            Loading...
          </Heading>
        )}
        {error && (
          <Heading size="lg" mx="auto">
            Error loading indicators
          </Heading>
        )}

        {!loading && !error && (
          <Stack
            direction={["column", "column", "row"]}
            spacing={[6, 6, 2]}
            w={["100%", "100%", "80%"]}
          >
            <ExportIndicatorList
              indicators={
                possibleIndicators?.filter(
                  (ind) => !selectedIndicators.includes(ind)
                ) ?? []
              }
              addSelected={addSelected}
              removeSelected={removeSelected}
              toggleSelected={toggleSelected}
            />
            {selectedIndicators && (
              <VStack
                overflow="scroll"
                align="stretch"
                w={["100%", "100%", "40%"]}
                h="50vh"
              >
                {selectedIndicators.length > 0 && (
                  <Heading size="md">Selected indicators</Heading>
                )}
                {selectedIndicators.length > 0
                  ? selectedIndicators.map((obj) => {
                      return (
                        <PossibleIndicatorBox
                          addSelected={addSelected}
                          removeSelected={removeSelected}
                          key={obj.id}
                          indicator={obj}
                          selected={true}
                          toggleSelect={() => toggleSelected(obj)}
                        />
                      );
                    })
                  : null}
              </VStack>
            )}
          </Stack>
        )}
        <ButtonGroup size="lg" isAttached>
          <Button
            leftIcon={<FaFileCsv />}
            fontSize="2xl"
            isActive={fileType === "csv"}
            onClick={() => setFileType("csv")}
          >
            CSV
          </Button>
          <Button
            leftIcon={<RiFileExcel2Fill color="green" />}
            fontSize="2xl"
            isActive={fileType === "excel"}
            onClick={() => setFileType("excel")}
            isDisabled
          >
            Excel
          </Button>
        </ButtonGroup>
        <Button
          cursor="pointer"
          colorScheme="green"
          w="60%"
          as="a"
          download
          isDisabled={selectedIndicators.length < 1}
          onClick={handleExport}
          loadingText="Exporting..."
          isLoading={fileLoad}
        >
          Download data
        </Button>
      </VStack>
    </Page>
  );
}
