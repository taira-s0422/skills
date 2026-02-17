---
name: excel-vba
description: Specializes in Excel VBA development, macro creation, automation, and workbook processing
user-invocable: true
argument-hint: "[task-description]"
---

# Excel VBA Development Skill

## Core Principles

### 必須事項
- `Option Explicit` を必ず宣言
- `On Error GoTo` によるエラーハンドリング
- `Application.ScreenUpdating` / `Application.Calculation` の制御
- 明示的な変数型宣言

### 標準テンプレート

```vba
Option Explicit

Sub ProcedureName()
    On Error GoTo ErrorHandler

    ' パフォーマンス最適化
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    ' メイン処理
    ' ...

Cleanup:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Exit Sub

ErrorHandler:
    MsgBox "エラー(" & Err.Number & "): " & Err.Description, vbCritical
    Resume Cleanup
End Sub
```

## 命名規則

- モジュール名: `mod_機能名` (例: mod_dataprocess)
- プロシージャ名: `動詞_対象` (例: export_data)
- 変数名: キャメルケース + 型プレフィックス
  - `str` - String
  - `lng` - Long
  - `rng` - Range
  - `ws` - Worksheet
  - `wb` - Workbook
  - `arr` - Array
  - `dic` - Dictionary
  - `col` - Collection

## よく使うパターン

### 最終行の取得

```vba
Dim lngLastRow As Long
lngLastRow = Cells(Rows.Count, "A").End(xlUp).Row
```

### 範囲ループ

```vba
Dim rngCell As Range
For Each rngCell In Range("A1:A" & lngLastRow)
    ' 処理
Next rngCell
```

### 配列処理（高速）

```vba
Dim arrData As Variant
arrData = Range("A1:Z" & lngLastRow).Value

Dim i As Long
For i = LBound(arrData, 1) To UBound(arrData, 1)
    ' arrData(i, 1) でアクセス
Next i

Range("A1:Z" & lngLastRow).Value = arrData
```

## パフォーマンス最適化

```vba
' 処理前
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Application.EnableEvents = False

' 処理後
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
Application.EnableEvents = True
```

## エラーハンドリングパターン

```vba
ErrorHandler:
    Dim strErrMsg As String
    strErrMsg = "エラー番号: " & Err.Number & vbCrLf & _
                "エラー内容: " & Err.Description & vbCrLf & _
                "発生箇所: " & Erl
    MsgBox strErrMsg, vbCritical, "エラー"
    Resume Cleanup
```

## 使用例

1. **VBAマクロ作成**: `/excel-vba 売上データを集計するマクロを作成`
2. **既存マクロの改善**: `/excel-vba このマクロを最適化して`
3. **自動化**: `/excel-vba 毎月の報告書を自動生成するマクロ`
4. **データ処理**: `/excel-vba CSVファイルを読み込んでExcelに整形`

## ガイドライン

1. すべての変数は `Dim` で明示的に宣言する
2. すべてのプロシージャにエラーハンドリングを実装する
3. 大量データ処理は配列を使用する
4. セル参照は `Range` または `Cells` を適切に使い分ける
5. マジックナンバーは定数（`Const`）で定義する
6. 処理の前後で `Application` プロパティを制御する
7. 長いプロシージャは適切にサブルーチンに分割する
8. 日本語コメントで処理内容を明記する

## 関連エージェント

複雑なVBA開発タスクには `@excel-vba-expert` エージェントを使用してください。
