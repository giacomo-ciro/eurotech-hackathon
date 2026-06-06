import { Nav } from "../components/Nav";

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Nav />
      <div className="flex-1 flex flex-col min-h-0">{children}</div>
    </>
  );
}
