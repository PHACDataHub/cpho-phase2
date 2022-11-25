import {
  Box,
  Editable,
  EditableInput,
  EditablePreview,
  Input,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";

const ValueTag = ({
  value,
  setValue,
}: {
  value: number;
  setValue: (val: number) => void;
}) => {
  const [tempValue, setTempValue] = useState(String(value));

  useEffect(() => {
    setTempValue(String(value));
  }, [value]);

  return (
    <Box bgColor="gray.100" p={2} borderRadius="md" display="inline-block">
      <Editable
        value={tempValue}
        onChange={(val) => setTempValue(val)}
        onSubmit={(val) => setValue(Number(val))}
      >
        <EditablePreview />
        <Input as={EditableInput} variant="unstyled" minW="4em" maxW="6em" />
      </Editable>
    </Box>
  );
};

export default ValueTag;
