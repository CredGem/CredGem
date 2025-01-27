import {useEffect, useState} from "react";
import {useWalletStore} from "@/store/useWalletStore";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Skeleton} from "@/components/ui/skeleton";
import {formatDate} from "@/lib/utils";
import {Badge} from "@/components/ui/badge";

export function SubscriptionsSection({walletId}: { walletId: string }) {
    const {subscriptions,  totalCount, fetchSubscriptions, error} = useWalletStore();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        (async () => {
            setIsLoading(true);
            await fetchSubscriptions(walletId, {
                page: 1,
                page_size: 100
            }).finally(() => {
                setIsLoading(false);
            });
        })()
    }, [walletId]);

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Subscriptions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <Skeleton className="h-20 w-full"/>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Subscriptions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-red-500">Error loading subscriptions: {error}</div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Subscriptions ({totalCount})</CardTitle>
            </CardHeader>
            <CardContent>
                {subscriptions.length === 0 ? (
                    <div className="text-muted-foreground">No active subscriptions</div>
                ) : (
                    <div className="space-y-4">
                        {subscriptions.map((subscription) => (
                            <div key={subscription.id} className="flex flex-col gap-2">
                                <h3 className="font-medium">{subscription.product?.name || 'Unknown Product'}</h3>
                                <div className="flex items-center gap-2">
                                    <Badge variant={subscription.status === "ACTIVE" ? "default" : "secondary"}>
                                        {subscription.status}
                                    </Badge>
                                    <span className="text-sm text-muted-foreground">
                                        Created {formatDate(subscription.created_at)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
} 