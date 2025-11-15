const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('help')
        .setDescription('Botun tüm komutlarını ve açıklamalarını listeler.'),
    async execute(interaction) {
        const embed = new EmbedBuilder()
            .setColor('#0099ff')
            .setTitle('📚 GAG Bot - Komut Listesi')
            .setDescription('Botun kullanabileceğiniz tüm komutlar aşağıda listelenmiştir.')
            .addFields(
                { name: '🛡️ Moderasyon', value: '`/timeout`, `/unmute`, `/ban`, `/kick`, `/unban`, `/softban`, `/clear`, `/purge`, `/slowmode`, `/lock`, `/unlock`, `/nick`', inline: false },
                { name: '🎮 Eğlence & Oyunlar', value: '`/gayrate`, `/yazıtura`, `/catfact`, `/meme`, `/drawgame`, `/guess`', inline: false },
                { name: '📊 Bilgi & Yardımcı', value: '`/weather`, `/serverinfo`, `/userinfo`, `/oyunlar`, `/help`', inline: false },
                { name: '🖼️ Görsel', value: '`/alıntıolustur`', inline: false },
                { name: '🎵 Müzik', value: '`/play`, `/skip`, `/stop`, `/queue`', inline: false },
                { name: '🎂 Doğum Günleri', value: '`/birthday`, `/birthdays`, `/birthdaychatroom`', inline: false },
                { name: '📰 Haberler & Kripto', value: '`/crypto`, `/haberrss`, `/habertest`', inline: false },
                { name: '🎮 PUBG', value: '`/pubgkanal`, `/pubg`', inline: false },
                { name: '⚙️ Ayarlar', value: '`/otorol`', inline: false }
            )
            .setFooter({ text: 'Komutlar hakkında daha fazla bilgi için /help <komut> yazabilirsiniz.' })
            .setTimestamp();

        await interaction.reply({ embeds: [embed] });
    }
};
