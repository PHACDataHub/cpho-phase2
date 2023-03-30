import {
  Button,
  ButtonGroup,
  Heading,
  Stack,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useState } from "react";
import { Page } from "../template/Page";
import { RiFileExcel2Fill } from "react-icons/ri";
import { FaFileCsv } from "react-icons/fa";
import { useMutation, useQuery } from "@apollo/client";
import { GET_INDICATOR_OVERVIEW } from "../../utils/graphql/queries";
import { PossibleIndicatorType } from "../../utils/types";
import PossibleIndicatorBox from "../molecules/PossibleIndicatorBox";
import ExportIndicatorList from "../organisms/ExportIndicatorList";
import { EXPORT_DATA } from "../../utils/graphql/mutations";

export function ExportPage() {
  const toast = useToast();
  const [fileType, setFileType] = useState<"excel" | "csv" | "sql">("csv");
  const [fileLoad, setFileLoad] = useState(false);

  const [selectedIndicators, setSelectedIndicators] = useState<
    PossibleIndicatorType[]
  >([]);

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

  const [exportData, { loading: exportLoading, error: exportError }] =
    useMutation(EXPORT_DATA);

  const handleExport = async () => {
    setFileLoad(true);
    try {
      const response = await exportData({
        variables: {
          selectedIndicators: selectedIndicators.map((ind) => ind.id),
        },
      });
      const fileUrl = response.data?.exportData?.csvFile?.fileUrl;
      if (!fileUrl) {
        throw new Error("No file url");
      }
      console.log(fileUrl);
      const link = document.createElement("a");
      link.setAttribute("href", fileUrl);
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
    } catch (error) {
      console.log(error);
      toast({
        title: "Error exporting data",
        description: "An error occured while exporting the data",
        status: "error",
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setFileLoad(false);
    }
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
