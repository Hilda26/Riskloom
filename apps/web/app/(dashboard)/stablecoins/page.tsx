import { StablecoinTable } from "@/components/dashboard/StablecoinTable";
import { getStablecoinsWithLiveData } from "@/lib/stablecoins";

export const revalidate = 0;

export default async function StablecoinsPage() {
  const items = await getStablecoinsWithLiveData();

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">All Stablecoins</div>
          <div className="dm-sub">{items.length} assets tracked - live prices via CoinGecko</div>
        </div>
      </div>
      <StablecoinTable items={items} />
    </>
  );
}
