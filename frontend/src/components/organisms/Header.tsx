import { HStack, Image } from "@chakra-ui/react";

export function Header(): JSX.Element {
  return (
    <>
      <HStack w="100%" display="flex" justify="space-between" p={5}>
        <Image maxWidth="400px" width="80%" src="/static/images/logo.svg" />
        {/* TODO: Implement language switcher */}
        {/* <ColorModeSwitcher /> */}
      </HStack>
      <hr
        style={{
          marginTop: 10,
          marginBottom: 10,
        }}
      />
    </>
  );
}
