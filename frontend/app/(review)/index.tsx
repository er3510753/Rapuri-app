import {
  StyleSheet,
  View,
  Platform,
  ScrollView,
  Alert,
  Dimensions,
  TouchableOpacity,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import React, { useState } from "react";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { IconSymbol } from "@/components/ui/IconSymbol";
import {
  TextInput as PaperTextInput,
  Button,
  Card,
  Surface,
  useTheme,
  Chip,
  IconButton,
} from "react-native-paper";
import { useLocalSearchParams, router } from "expo-router";
import * as ImagePicker from "expo-image-picker";
import { Image } from "expo-image";

const { width: screenWidth } = Dimensions.get("window");

// レストラン情報の型定義(仮)
interface RestaurantInfo {
  id: string;
  name: string;
  address?: string;
  rating?: number;
  popularTaste?: string;
  photoUrl?: string;
}

// ユーザー情報の型定義
interface UserInfo {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

// フロントエンド用の完全なレビューデータの型定義
interface ReviewData {
  id?: number;
  restaurantId: string;
  restaurantName: string;
  userId: string;
  userName: string;
  menu: string;
  rating: number;
  noodleHardness: string;
  soupRichness: string;
  review: string;
  photo: string;
  createdAt: Date;
  createdDate: string; // YYYY-MM-DD形式
  createdTime: string; // HH:MM形式
}

// バックエンドとのやり取り用の型定義（現在のRamenLogモデルに合わせる）
interface ReviewDataForAPI {
  id?: number;
  shop_name: string;
  user: number; // ユーザーID
  ordered_item: string;
  rating: number;
  visited_at: string; // ISO 8601形式の日時文字列
  soup_richness?: string;
  // 備考: 以下のフィールドはバックエンドのモデルに合わせて追加・削除してください
  noodle_hardness?: string;
  toppings?: string;
}

export default function ReviewScreen() {
  // 本来はマップから取得
  // const params = useLocalSearchParams();

  // 店舗データ(仮)
  const params = {
    id: "1",
    name: "ラーメン太郎",
    address: "東京都千代田区永田町1-7-1",
    rating: 4.5,
    popularTaste: "醤油",
    photoUrl:
      "https://t4.ftcdn.net/jpg/03/84/51/99/360_F_384519931_4aCpUpvu9X2lIWwfXUbLAFIw6UfSrM8m.jpg",
  };

  const restaurantInfo: RestaurantInfo = {
    id: (params.id as string) || "",
    name: (params.name as string) || "",
    address: (params.address as string) || "",
    rating: params.rating
      ? parseFloat(params.rating as unknown as string)
      : undefined,
    popularTaste: `おすすめ：${params.popularTaste as string}` || "",
    photoUrl: (params.photoUrl as string) || "",
  };

  // ユーザー情報(どっかから取得する)
  const isLoggedIn = true;
  const userInfo = {
    // 修正点: バックエンドのUserモデルのID(数値)に合わせてください。例: '1'
    // `python manage.py shell` で `from users.models import User; User.objects.first().id` などで確認できます。
    id: "1",
    name: "ラーメン大好き",
    email: "ramen@example.com",
    avatar:
      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
  };

  // レビュー情報
  const [menuName, setMenuName] = useState("");
  const [rating, setRating] = useState(5);
  const [noodleHardness, setNoodleHardness] = useState<string>("");
  const [soupRichness, setSoupRichness] = useState<string>("");
  const [selectedToppings, setSelectedToppings] = useState<string[]>([]);
  const [isToppingsOpen, setIsToppingsOpen] = useState(false);
  const [review, setReview] = useState("");
  const [photoUri, setPhotoUri] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const theme = useTheme();

  const handleClose = () => {
    router.back();
  };

  // 撮影機能
  const takePhoto = async () => {
    // カメラの権限をリクエスト
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("カメラのアクセスが許可されていません");
      return;
    }
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });
      if (!result.canceled && result.assets && result.assets.length > 0) {
        setPhotoUri(result.assets[0].uri);
      } else if (result.canceled) {
        // キャンセル時は何もしない
      } else {
        Alert.alert("写真の取得に失敗しました");
      }
    } catch (error) {
      Alert.alert("エラー", "カメラの起動に失敗しました");
    }
  };

  const selectPhotoFromGallery = async () => {
    // TODO: ギャラリーから写真選択実装
    console.log("ギャラリーから選択");
    Alert.alert("写真選択", "ギャラリー機能は後で実装予定");
  };

  const submitReview = async () => {
    if (!isLoggedIn || !userInfo) {
      console.log("ログインが必要");
      Alert.alert(
        "ログインが必要",
        "レビューを投稿するにはログインしてください"
      );
      return;
    }

    if (!menuName) {
      Alert.alert("メニュー名を入力してください");
      return;
    }

    setIsSubmitting(true);
    try {
      const now = new Date();

      // バックエンドとのやり取り用のデータを作成
      const apiData: ReviewDataForAPI = {
        shop_name: restaurantInfo.name,
        // 修正点: userはバックエンドで自動的に割り当てるのが理想ですが、
        // 今回は動作確認のため、フロントから送信します。parseIntの基数を指定します。
        user: parseInt(userInfo.id, 10),
        ordered_item: menuName,
        rating: rating,
        visited_at: now.toISOString(),
        noodle_hardness: noodleHardness,
        soup_richness: soupRichness,
        toppings: selectedToppings.join(", "),
      };

      // バックエンドAPIに投稿
      // .env ファイルからAPIのURLを読み込むように修正
      const apiUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/ramen/ramenlog/`;
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // TODO: 認証トークンを追加
          // 'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(apiData),
      });

      if (!response.ok) {
        // バックエンドからの詳細なエラーメッセージを組み立てる
        let errorMessage = `APIエラー (ステータス: ${response.status})`;
        try {
          const errorData = await response.json();
          console.error("API Error Data:", errorData);
          const details = Object.entries(errorData)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('\n');
          errorMessage += `\n${details}`;
        } catch (e) {
          // JSONのパースに失敗した場合
          errorMessage += `\nレスポンスの解析に失敗しました。`;
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log("API Response:", result);
      console.log("バックエンド用データ:", apiData);

      Alert.alert("成功", "レビューを投稿しました！");
      // フォームをリセット
      setMenuName("");
      setRating(5);
      setNoodleHardness("");
      setSoupRichness("");
      setSelectedToppings([]);
      setReview("");
      setPhotoUri("");
    } catch (error) {
      console.error("Submit Error:", error);
      Alert.alert("投稿エラー", error instanceof Error ? error.message : "不明なエラーが発生しました。");
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStarRating = () => {
    return (
      <View style={styles.ratingContainer}>
        <View style={styles.starsContainer}>
          {[1, 2, 3, 4, 5].map((star) => (
            <TouchableOpacity
              key={star}
              onPress={() => setRating(star)}
              style={styles.starButton}
              activeOpacity={0.7}
            >
              <IconSymbol
                size={32}
                name={star <= rating ? "star.fill" : "star"}
                color={star <= rating ? "#FFD700" : "#C0C0C0"}
              />
            </TouchableOpacity>
          ))}
        </View>
        <ThemedText style={styles.ratingText}>{rating}/5</ThemedText>
      </View>
    );
  };

  const renderNoodleHardness = () => {
    const options = ["やわめ", "ふつう", "かため"];
    return (
      <View style={styles.optionContainer}>
        <ThemedText type="defaultSemiBold" style={styles.subSectionTitle}>
          麺の硬さ
        </ThemedText>
        <View style={styles.buttonGroup}>
          {options.map((option) => (
            <Button
              key={option}
              mode={noodleHardness === option ? "contained" : "outlined"}
              onPress={() => setNoodleHardness(option)}
              style={styles.optionButton}
              labelStyle={styles.optionButtonLabel}
            >
              {option}
            </Button>
          ))}
        </View>
      </View>
    );
  };

  const renderSoupRichness = () => {
    const options = ["あっさり", "ふつう", "こってり"];
    return (
      <View style={styles.optionContainer}>
        <ThemedText type="defaultSemiBold" style={styles.subSectionTitle}>
          スープの濃さ
        </ThemedText>
        <View style={styles.buttonGroup}>
          {options.map((option) => (
            <Button
              key={option}
              mode={soupRichness === option ? "contained" : "outlined"}
              onPress={() => setSoupRichness(option)}
              style={styles.optionButton}
              labelStyle={styles.optionButtonLabel}
            >
              {option}
            </Button>
          ))}
        </View>
      </View>
    );
  };

  const renderToppings = () => {
    const toppingOptions = [
      "チャーシュー",
      "メンマ",
      "ネギ",
      "たまご",
      "海苔",
      "トウモロコシ",
      "もやし",
      "バター",
      "ほうれん草",
    ];

    const toggleTopping = (topping: string) => {
      setSelectedToppings((prev) =>
        prev.includes(topping)
          ? prev.filter((t) => t !== topping)
          : [...prev, topping]
      );
    };

    return (
      <View style={styles.optionContainer}>
        <View style={styles.toppingsHeader}>
          <ThemedText type="defaultSemiBold" style={styles.subSectionTitle}>
            トッピング
          </ThemedText>
          <IconButton
            icon={isToppingsOpen ? "minus-circle" : "plus-circle"}
            size={24}
            iconColor="#007AFF"
            style={styles.toppingsToggleIcon}
            onPress={() => setIsToppingsOpen(!isToppingsOpen)}
          />
        </View>

        {isToppingsOpen && (
          <View style={styles.toppingsContainer}>
            {toppingOptions.map((topping) => (
              <Chip
                key={topping}
                selected={selectedToppings.includes(topping)}
                onPress={() => toggleTopping(topping)}
                style={styles.toppingChip}
                textStyle={styles.toppingChipText}
              >
                {topping}
              </Chip>
            ))}
          </View>
        )}
        {selectedToppings.length > 0 && (
          <ThemedText style={styles.selectedToppingsText}>
            選択中: {selectedToppings.join(", ")}
          </ThemedText>
        )}
      </View>
    );
  };

  const renderRestaurantInfo = () => {
    return (
      <Card style={styles.restaurantCard}>
        <Card.Content>
          <View style={styles.restaurantHeader}>
            <View style={styles.restaurantTextContainer}>
              <ThemedText type="title" style={styles.restaurantName}>
                {restaurantInfo.name}
              </ThemedText>
              {restaurantInfo.address && (
                <ThemedText style={styles.restaurantAddress}>
                  📍 {restaurantInfo.address}
                </ThemedText>
              )}
            </View>
            {restaurantInfo.photoUrl && (
              <Image
                source={{ uri: restaurantInfo.photoUrl }}
                style={styles.restaurantImage}
                contentFit="cover"
              />
            )}
          </View>
          <View style={styles.restaurantChips}>
            {restaurantInfo.rating && (
              <Chip icon="star" style={styles.chip}>
                {restaurantInfo.rating.toFixed(1)}
              </Chip>
            )}
            {restaurantInfo.popularTaste && (
              <Chip icon="food" style={styles.chip}>
                {restaurantInfo.popularTaste}
              </Chip>
            )}
          </View>
        </Card.Content>
      </Card>
    );
  };

  return (
    <ThemedView style={styles.container}>
      <StatusBar style="auto" />

      {/* ヘッダー */}
      <View style={styles.header}>
        <IconButton
          icon="close"
          size={24}
          onPress={handleClose}
          style={styles.closeButton}
          iconColor="#333"
        />
        <ThemedText type="title" style={styles.headerTitle}>
          ラーメン記録
        </ThemedText>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <Surface style={styles.surface} elevation={2}>
          {/* レストラン情報 */}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            店名
          </ThemedText>
          {renderRestaurantInfo()}

          {/* メニュー名 */}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            メニュー名 *
          </ThemedText>
          <PaperTextInput
            label="入力してください"
            value={menuName}
            onChangeText={setMenuName}
            placeholder="例: 醤油ラーメン"
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="next"
          />

          {/* 評価 */}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            評価
          </ThemedText>
          {renderStarRating()}

          {/*味の詳細*/}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            味の詳細
          </ThemedText>
          {renderNoodleHardness()}
          {renderSoupRichness()}
          {renderToppings()}

          {/* 写真 */}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            写真
          </ThemedText>
          <View style={styles.photoButtonsContainer}>
            <Button
              mode="outlined"
              icon="camera"
              onPress={takePhoto}
              style={styles.photoButton}
              contentStyle={{ flexDirection: "row-reverse" }}
            >
              撮影
            </Button>
            <Button
              mode="outlined"
              icon="image"
              onPress={selectPhotoFromGallery}
              style={styles.photoButton}
              contentStyle={{ flexDirection: "row-reverse" }}
            >
              選択
            </Button>
          </View>
          {photoUri ? (
            <Card style={styles.photoPreview}>
              <Card.Content>
                <ThemedText>写真が選択されました</ThemedText>
              </Card.Content>
            </Card>
          ) : null}

          {/* 感想 */}
          <ThemedText type="defaultSemiBold" style={styles.sectionTitle}>
            感想
          </ThemedText>
          <PaperTextInput
            label="入力してください(任意)"
            value={review}
            onChangeText={setReview}
            placeholder="ラーメンの感想を書いてください..."
            mode="outlined"
            style={[styles.input, styles.textArea]}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            autoCapitalize="sentences"
          />

          {/* 投稿ボタン */}
          <Button
            mode="contained"
            onPress={submitReview}
            loading={isSubmitting}
            disabled={isSubmitting}
            style={styles.submitButton}
            contentStyle={{ height: 56 }}
            labelStyle={{ fontSize: 18, fontWeight: "bold", color: "#fff" }}
          >
            {isSubmitting ? "投稿中..." : "レビューを投稿"}
          </Button>
        </Surface>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: Platform.OS === "ios" ? 50 : 30,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  closeButton: {
    margin: 0,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    flex: 1,
    textAlign: "center",
  },
  headerSpacer: {
    width: 48, // closeButtonと同じ幅
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 100,
    alignItems: "center",
  },
  surface: {
    width: "100%",
    maxWidth: 500,
    borderRadius: 16,
    padding: 20,
    backgroundColor: "#fff",
    marginBottom: 30,
    elevation: 2,
  },
  restaurantCard: {
    marginBottom: 20,
    borderRadius: 12,
    backgroundColor: "#f8f9fa",
  },
  restaurantHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  restaurantTextContainer: {
    flex: 1,
  },
  restaurantName: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 4,
  },
  restaurantAddress: {
    fontSize: 14,
    color: "#666",
  },
  restaurantImage: {
    width: 80,
    height: 80,
    borderRadius: 12,
    objectFit: "cover",
  },
  restaurantChips: {
    flexDirection: "row",
    gap: 8,
  },
  chip: {
    marginRight: 8,
  },
  input: {
    marginBottom: 16,
    backgroundColor: "#fff",
  },
  textArea: {
    minHeight: 100,
    paddingTop: 8,
  },
  ratingContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 10,
    marginBottom: 10,
    justifyContent: "center",
  },
  ratingLabel: {
    marginRight: 15,
    fontSize: 16,
  },
  starsContainer: {
    flexDirection: "row",
    marginRight: 15,
  },
  starButton: {
    marginHorizontal: 5,
    padding: 5,
    minWidth: 40,
    alignItems: "center",
    justifyContent: "center",
  },
  ratingText: {
    fontSize: 18,
    fontWeight: "bold",
  },
  optionContainer: {
    marginTop: 10,
    marginBottom: 10,
  },
  subSectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 8,
    color: "#333",
  },
  buttonGroup: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 8,
  },
  optionButton: {
    borderRadius: 8,
    minWidth: 90,
    paddingHorizontal: 0,
    flex: 0,
    alignItems: "center",
    justifyContent: "center",
  },
  optionButtonLabel: {
    fontSize: 14,
    fontWeight: "bold",
    textAlign: "center",
    letterSpacing: 0,
  },
  photoButtonsContainer: {
    flexDirection: "row",
    gap: 12,
    marginTop: 10,
    marginBottom: 10,
  },
  photoButton: {
    flex: 1,
    marginHorizontal: 2,
    borderRadius: 8,
  },
  photoPreview: {
    marginTop: 12,
    borderRadius: 12,
    backgroundColor: "#f8f9fa",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#e9ecef",
  },
  submitButton: {
    marginTop: 24,
    borderRadius: 12,
    minHeight: 56,
    justifyContent: "center",
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 8,
    marginTop: 16,
    color: "#333",
  },
  toppingsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 8,
  },
  toppingChip: {
    marginBottom: 4,
  },
  toppingChipText: {
    fontSize: 14,
  },
  selectedToppingsText: {
    fontSize: 14,
    color: "#666",
    fontStyle: "italic",
    marginTop: 4,
  },
  toppingsHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  toppingsToggleButton: {
    padding: 4,
  },
  toppingsToggleIcon: {
    margin: 0,
  },
});
