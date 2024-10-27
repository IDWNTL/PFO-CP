import Header from "@/app/components/Header";
import BodyPage from "@/app/components/Body";

export default function Home() {
    return (
        <div className="flex flex-col h-screen justify-center items-center overflow-y-hidden">
            <Header />
            <BodyPage />
        </div>
    );
}