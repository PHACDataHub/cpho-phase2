import { useQuery } from "@apollo/client";
import { useParams } from "react-router-dom";
import IndicatorForm from "../organisms/IndicatorForm";
import { Page } from "../template/Page";
import { GET_INDICATOR_DATA } from "../../utils/graphql/queries";
import { Spinner, Text } from "@chakra-ui/react";
import { IndicatorType } from "../../utils/types";

const ModifyIndicator = () => {
  const { id } = useParams();

  const { data, loading, error } = useQuery<{
    indicator: IndicatorType;
  }>(GET_INDICATOR_DATA, {
    variables: {
      id: Number(id),
    },
    fetchPolicy: "network-only",
  });

  const name = data?.indicator.name.toLocaleLowerCase() ?? id;

  return (
    <Page
      backButton={{ show: true, redirectUrl: "/past-submissions" }}
      title={`Modify Indicator ${name}`}
    >
      {loading && <Spinner />}
      {error && <Text>Could not load indicator</Text>}
      {data && <IndicatorForm indicator={data?.indicator} mode="modify" />}
    </Page>
  );
};

export default ModifyIndicator;
